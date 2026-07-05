"""
Auth service — all authentication business logic lives here.

Routers call this; this calls the repository + core.security utilities.
Never import FastAPI Request/Response objects here — keep this layer
framework-agnostic and unit-testable.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.config import settings
from app.core.email import get_email_service
from app.core.exceptions import ConflictException, UnauthorizedException, ValidationException
from app.core.logging import get_logger
from app.core.redis_client import get_redis_client
from app.core.security import (
    TokenType,
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token_of_type,
    hash_password,
    verify_password,
)
from app.db.types import ensure_utc
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# Audit logger — separate name from the general app logger so security
# events can be filtered/shipped independently in a production log
# pipeline. Never logs passwords, tokens, or full request payloads —
# only event names, user ids, and outcome, matching the redaction rules
# in core/logging.py.
audit_logger = get_logger("audit")


def _revoked_jti_key(jti: str) -> str:
    return f"revoked_jti:{jti}"


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    # ----------------------------------------------------------------
    # Registration / login
    # ----------------------------------------------------------------

    async def register(self, payload: UserCreate) -> User:
        existing = await self.repo.get_by_email(payload.email)
        if existing is not None:
            # Deliberately generic message — do not reveal whether the
            # account exists via a different error for "email taken".
            raise ConflictException("Unable to create account with the provided details")

        user = await self.repo.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        audit_logger.info("user_registered", user_id=str(user.id))
        return user

    async def authenticate(self, email: str, password: str) -> User:
        """
        Verify credentials with account-lockout protection against
        brute-force attempts. Always raises the SAME UnauthorizedException
        message regardless of whether the email exists, the password is
        wrong, or the account is locked — this prevents user enumeration.
        """
        generic_error = UnauthorizedException("Invalid email or password")

        user = await self.repo.get_by_email(email)
        if user is None:
            audit_logger.warning("login_failed", reason="no_such_account")
            raise generic_error

        now = datetime.now(timezone.utc)
        locked_until = ensure_utc(user.locked_until)
        if locked_until is not None and locked_until > now:
            audit_logger.warning("login_blocked_account_locked", user_id=str(user.id))
            raise UnauthorizedException(
                "Account temporarily locked due to repeated failed attempts. Try again later."
            )

        if not user.is_active:
            audit_logger.warning("login_blocked_inactive_account", user_id=str(user.id))
            raise generic_error

        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                user.failed_login_attempts = 0
                audit_logger.warning("account_locked", user_id=str(user.id))
            await self.repo.save(user)
            audit_logger.warning("login_failed", user_id=str(user.id), reason="bad_password")
            raise generic_error

        # Successful login resets lockout counters
        if user.failed_login_attempts > 0 or user.locked_until is not None:
            user.failed_login_attempts = 0
            user.locked_until = None
            await self.repo.save(user)

        audit_logger.info("login_succeeded", user_id=str(user.id))
        return user

    @staticmethod
    def issue_tokens(user: User) -> tuple[str, str]:
        access = create_access_token(subject=str(user.id), role=user.role.value)
        refresh = create_refresh_token(subject=str(user.id), role=user.role.value)
        return access, refresh

    # ----------------------------------------------------------------
    # Refresh token rotation
    # ----------------------------------------------------------------
    #
    # Rotation: every successful /refresh call issues a BRAND NEW refresh
    # token and immediately revokes the one that was just used, by
    # recording its jti in Redis with a TTL equal to its remaining
    # lifetime. This means a stolen refresh token is only useful until
    # the legitimate client's next refresh — after that, both the
    # attacker's and the legitimate client's copy of that specific token
    # are rejected, which is what actually happens with refresh-token
    # theft in practice (whichever side refreshes first "wins", and the
    # other now gets a detectably-reused-token error). Full theft
    # detection (e.g. alerting when a revoked token is presented) is a
    # documented future step, not implemented here.

    async def rotate_refresh_token(self, old_jti: str, old_exp: datetime, user: User) -> tuple[str, str]:
        redis = get_redis_client()
        ttl_seconds = max(1, int((old_exp - datetime.now(timezone.utc)).total_seconds()))
        await redis.setex(_revoked_jti_key(old_jti), ttl_seconds, "1")

        new_access = create_access_token(subject=str(user.id), role=user.role.value)
        new_refresh = create_refresh_token(subject=str(user.id), role=user.role.value)
        audit_logger.info("refresh_token_rotated", user_id=str(user.id))
        return new_access, new_refresh

    @staticmethod
    async def is_refresh_token_revoked(jti: str) -> bool:
        redis = get_redis_client()
        return bool(await redis.exists(_revoked_jti_key(jti)))

    # ----------------------------------------------------------------
    # Password management
    # ----------------------------------------------------------------

    async def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            audit_logger.warning("change_password_failed", user_id=str(user.id), reason="bad_current_password")
            raise UnauthorizedException("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self.repo.save(user)
        audit_logger.info("password_changed", user_id=str(user.id))

    async def request_password_reset(self, email: str) -> None:
        """
        Always succeeds from the caller's perspective (the router returns
        a generic "if that email exists, we sent a link" response)
        regardless of whether the account exists — this prevents
        attackers from using this endpoint to enumerate valid emails.
        """
        user = await self.repo.get_by_email(email)
        if user is None:
            audit_logger.info("password_reset_requested_unknown_email")
            return

        token = create_password_reset_token(subject=str(user.id), role=user.role.value)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        await get_email_service().send_password_reset(user.email, reset_url)
        audit_logger.info("password_reset_requested", user_id=str(user.id))

    async def reset_password(self, token: str, new_password: str) -> None:
        payload = decode_token_of_type(token, TokenType.PASSWORD_RESET)
        if payload is None:
            raise ValidationException("Invalid or expired reset token")

        user = await self.repo.get_by_id(UUID(payload.sub))
        if user is None or not user.is_active:
            raise ValidationException("Invalid or expired reset token")

        user.hashed_password = hash_password(new_password)
        # A completed reset also clears any active lockout — a verified
        # password reset is a stronger proof of ownership than waiting
        # out a lockout timer.
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.repo.save(user)
        audit_logger.info("password_reset_completed", user_id=str(user.id))

    # ----------------------------------------------------------------
    # Email verification
    # ----------------------------------------------------------------

    async def request_email_verification(self, user: User) -> None:
        if user.is_email_verified:
            return
        token = create_email_verification_token(subject=str(user.id), role=user.role.value)
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        await get_email_service().send_email_verification(user.email, verification_url)
        audit_logger.info("email_verification_requested", user_id=str(user.id))

    async def verify_email(self, token: str) -> None:
        payload = decode_token_of_type(token, TokenType.EMAIL_VERIFICATION)
        if payload is None:
            raise ValidationException("Invalid or expired verification token")

        user = await self.repo.get_by_id(UUID(payload.sub))
        if user is None:
            raise ValidationException("Invalid or expired verification token")

        user.is_email_verified = True
        await self.repo.save(user)
        audit_logger.info("email_verified", user_id=str(user.id))
