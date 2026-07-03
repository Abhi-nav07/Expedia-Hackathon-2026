"""
Auth service — all authentication business logic lives here.

Routers call this; this calls the repository + core.security utilities.
Never import FastAPI Request/Response objects here — keep this layer
framework-agnostic and unit-testable.
"""
from datetime import datetime, timedelta, timezone

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

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
            raise generic_error

        now = datetime.now(timezone.utc)
        if user.locked_until is not None and user.locked_until > now:
            raise UnauthorizedException(
                "Account temporarily locked due to repeated failed attempts. Try again later."
            )

        if not user.is_active:
            raise generic_error

        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                user.failed_login_attempts = 0
            await self.repo.save(user)
            raise generic_error

        # Successful login resets lockout counters
        if user.failed_login_attempts > 0 or user.locked_until is not None:
            user.failed_login_attempts = 0
            user.locked_until = None
            await self.repo.save(user)

        return user

    @staticmethod
    def issue_tokens(user: User) -> tuple[str, str]:
        access = create_access_token(subject=str(user.id), role=user.role.value)
        refresh = create_refresh_token(subject=str(user.id), role=user.role.value)
        return access, refresh

    async def refresh_access_token(self, user_id: str, role: str) -> str:
        return create_access_token(subject=user_id, role=role)
