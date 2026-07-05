"""
Auth router. HTTP concerns only — validation via Pydantic, delegation to
AuthService for everything else. No SQLAlchemy or password logic here.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_user_repository
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.redis_client import get_redis_client
from app.core.security import TokenType, decode_token_of_type
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    EmailVerificationConfirm,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth/refresh",
    )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
    description=(
        "Creates a new user account with a hashed (Argon2) password. "
        "Returns the created user — does NOT log the user in; call "
        "/auth/login afterward. Rate limited to 10 requests/minute per IP."
    ),
    responses={
        201: {"description": "Account created successfully."},
        409: {"description": "An account with these details could not be created."},
        422: {"description": "Validation failed (weak password, invalid email, etc.)."},
        429: {"description": "Rate limit exceeded."},
    },
)
@limiter.limit("10/minute")
async def register(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> UserRead:
    user = await service.register(payload)
    await db.commit()
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in",
    description=(
        "Authenticates with email + password. On success, sets an httpOnly "
        "`refresh_token` cookie (scoped to /api/v1/auth/refresh) and returns "
        "a short-lived access token in the response body. Accounts are "
        "locked for 15 minutes after 5 consecutive failed attempts. Rate "
        "limited to 5 requests/minute per IP."
    ),
    responses={
        200: {"description": "Login successful."},
        401: {"description": "Invalid credentials, inactive account, or account locked."},
        429: {"description": "Rate limit exceeded."},
    },
)
@limiter.limit("5/minute")  # stricter than the global default — brute-force surface
async def login(
    request: Request,
    response: Response,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        user = await service.authenticate(payload.email, payload.password)
    except Exception:
        # authenticate() deliberately raises on bad credentials/lockout,
        # but it may have ALREADY written a legitimate side effect first
        # (incrementing failed_login_attempts, or setting locked_until) via
        # repo.save(). get_db()'s dependency generator rolls back on ANY
        # exception propagating out of this endpoint — including this
        # expected one — which would otherwise silently discard that
        # counter write every time, permanently disabling account
        # lockout. Commit here, before re-raising, so the counter/lockout
        # state persists regardless of the auth outcome. This is scoped
        # to this endpoint specifically rather than changing get_db()'s
        # rollback-on-exception behavior globally, which is the correct
        # safe default for every other endpoint (e.g. register() should
        # NOT partially commit on a duplicate-email failure).
        await db.commit()
        raise
    await db.commit()  # persist lockout-counter reset on successful login

    access_token, refresh_token = service.issue_tokens(user)

    # Refresh token goes in an httpOnly cookie — never in JS-readable storage,
    # so it can't be exfiltrated via XSS. Access token goes in the JSON body;
    # the frontend keeps it in memory only (see docs/02-architecture.md).
    _set_refresh_cookie(response, refresh_token)

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and issue a new access token",
    description=(
        "Exchanges a valid, non-revoked refresh token for a new access "
        "token AND a new refresh token (rotation). The refresh token just "
        "used is immediately revoked (tracked in Redis until its natural "
        "expiry) — reusing it after this call fails with 401. Browser "
        "clients rely on the httpOnly cookie; non-browser clients may pass "
        "`refresh_token` in the body instead."
    ),
    responses={
        200: {"description": "New access + refresh token issued."},
        401: {"description": "Missing, invalid, expired, or already-rotated refresh token."},
        429: {"description": "Rate limit exceeded."},
    },
)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    repo: UserRepository = Depends(get_user_repository),
    service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    # Browser clients send the httpOnly cookie automatically; non-browser
    # clients (mobile, server-to-server) may send it in the request body.
    raw_token = refresh_token_cookie or (payload.refresh_token if payload else None)
    if raw_token is None:
        raise UnauthorizedException("Refresh token is required")

    token_payload = decode_token_of_type(raw_token, TokenType.REFRESH)
    if token_payload is None:
        raise UnauthorizedException("Invalid or expired refresh token")

    if await AuthService.is_refresh_token_revoked(token_payload.jti):
        # This refresh token was already used once (rotation already
        # consumed it) — either a replay attack or a client retrying a
        # stale token. Either way, do not honor it.
        raise UnauthorizedException("Refresh token has already been used")

    user = await repo.get_by_id(uuid.UUID(token_payload.sub))
    if user is None or not user.is_active:
        raise UnauthorizedException("Account is inactive or no longer exists")

    new_access_token, new_refresh_token = await service.rotate_refresh_token(
        old_jti=token_payload.jti, old_exp=token_payload.exp, user=user
    )
    _set_refresh_cookie(response, new_refresh_token)

    return TokenResponse(access_token=new_access_token, user=UserRead.model_validate(user))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user",
    description="Returns the profile of the user identified by the Bearer access token.",
    responses={200: {"description": "Current user."}, 401: {"description": "Not authenticated."}},
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out",
    description=(
        "Clears the refresh-token cookie client-side. With short-lived "
        "access tokens, logout is primarily a client action; this endpoint "
        "additionally revokes the caller's most recent refresh token jti if "
        "one is present, so a stolen access token can't be used to keep "
        "silently refreshing after the user has explicitly logged out."
    ),
    responses={204: {"description": "Logged out."}, 401: {"description": "Not authenticated."}},
)
async def logout(
    response: Response,
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    current_user: User = Depends(get_current_user),
) -> None:
    if refresh_token_cookie:
        payload = decode_token_of_type(refresh_token_cookie, TokenType.REFRESH)
        if payload is not None:
            redis = get_redis_client()
            ttl_seconds = max(1, int((payload.exp - datetime.now(timezone.utc)).total_seconds()))
            await redis.setex(f"revoked_jti:{payload.jti}", ttl_seconds, "1")

    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    return None


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password (authenticated)",
    description=(
        "Changes the current user's password. Requires the current "
        "password as proof of ownership (as opposed to /reset-password, "
        "which proves ownership via an emailed token instead)."
    ),
    responses={
        204: {"description": "Password changed."},
        401: {"description": "Current password incorrect, or not authenticated."},
        422: {"description": "New password does not meet complexity requirements."},
    },
)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.change_password(current_user, payload.current_password, payload.new_password)
    await db.commit()
    return None


@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request a password reset email",
    description=(
        "Always returns 202 regardless of whether the email is registered "
        "— this prevents attackers from using this endpoint to discover "
        "which emails have accounts. If the account exists, a reset link "
        "(valid for PASSWORD_RESET_TOKEN_EXPIRE_MINUTES) is sent via the "
        "configured EmailService (console-logged in local/dev)."
    ),
    responses={202: {"description": "Request accepted."}, 429: {"description": "Rate limit exceeded."}},
)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    payload: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    await service.request_password_reset(payload.email)
    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Complete a password reset",
    description="Consumes a password-reset token (from the emailed link) and sets a new password.",
    responses={
        204: {"description": "Password reset."},
        422: {"description": "Invalid, expired token, or new password fails complexity check."},
    },
)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.reset_password(payload.token, payload.new_password)
    await db.commit()
    return None


@router.post(
    "/resend-verification",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Resend the email verification link",
    description="Requires authentication. No-ops if the account is already verified.",
    responses={202: {"description": "Request accepted."}, 401: {"description": "Not authenticated."}},
)
@limiter.limit("5/minute")
async def resend_verification(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    await service.request_email_verification(current_user)
    return {"message": "Verification email sent if the account is not already verified."}


@router.post(
    "/verify-email",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Complete email verification",
    description="Consumes an email-verification token (from the emailed link) and marks the account verified.",
    responses={204: {"description": "Email verified."}, 422: {"description": "Invalid or expired token."}},
)
async def verify_email(
    payload: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.verify_email(payload.token)
    await db.commit()
    return None
