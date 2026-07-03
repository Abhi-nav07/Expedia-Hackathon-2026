"""
Auth router. HTTP concerns only — validation via Pydantic, delegation to
AuthService for everything else. No SQLAlchemy or password logic here.
"""
import uuid

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_user_repository
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import TokenType, decode_token_of_type
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
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


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
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


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # stricter than the global default — brute-force surface
async def login(
    request: Request,
    response: Response,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    user = await service.authenticate(payload.email, payload.password)
    await db.commit()  # persist lockout-counter reset if it changed

    access_token, refresh_token = service.issue_tokens(user)

    # Refresh token goes in an httpOnly cookie — never in JS-readable storage,
    # so it can't be exfiltrated via XSS. Access token goes in the JSON body;
    # the frontend keeps it in memory only (see docs/02-architecture.md).
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth/refresh",
    )

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    payload: RefreshRequest | None = None,
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    repo: UserRepository = Depends(get_user_repository),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    # Browser clients send the httpOnly cookie automatically; non-browser
    # clients (mobile, server-to-server) may send it in the request body.
    raw_token = refresh_token_cookie or (payload.refresh_token if payload else None)
    if raw_token is None:
        raise UnauthorizedException("Refresh token is required")

    token_payload = decode_token_of_type(raw_token, TokenType.REFRESH)
    if token_payload is None:
        raise UnauthorizedException("Invalid or expired refresh token")

    user = await repo.get_by_id(uuid.UUID(token_payload.sub))
    if user is None or not user.is_active:
        raise UnauthorizedException("Account is inactive or no longer exists")

    new_access_token = await service.refresh_access_token(str(user.id), user.role.value)
    return TokenResponse(access_token=new_access_token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)) -> None:
    """
    With short-lived access tokens and no server-side session, logout is
    primarily a client-side action (discard tokens / clear cookie). This
    endpoint exists as an extension point for token-blacklisting via Redis
    if the future challenge requires immediate revocation — the `jti` claim
    on every token (see core/security.py) is already in place for that.
    """
    return None
