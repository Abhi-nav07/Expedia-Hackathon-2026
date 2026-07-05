"""
Auth-related Pydantic schemas.

Kept strictly separate from app.models.user.User (the ORM model) so the
API contract can evolve independently of the DB schema.
"""
import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


def validate_password_complexity(v: str) -> str:
    """
    OWASP-aligned complexity check, shared by every schema that accepts a
    new password (UserCreate, PasswordResetConfirm, ChangePasswordRequest).
    Previously duplicated across two schemas; refactored here rather than
    copy-pasted a third and fourth time.
    """
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", v):
        raise ValueError("Password must contain at least one digit")
    return v


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=10, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)

    _validate_password = field_validator("password")(validate_password_complexity)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_email_verified: bool
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshRequest(BaseModel):
    """Body fallback for clients that can't rely on the httpOnly cookie
    (mobile apps, server-to-server) — see routers/auth.py's /refresh."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """POST /auth/forgot-password body."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """POST /auth/reset-password body."""
    token: str
    new_password: str = Field(..., min_length=10, max_length=128)

    _validate_password = field_validator("new_password")(validate_password_complexity)


class ChangePasswordRequest(BaseModel):
    """POST /auth/change-password body — requires the current password,
    unlike a reset (which proves identity via the emailed token instead)."""
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=10, max_length=128)

    _validate_password = field_validator("new_password")(validate_password_complexity)


class EmailVerificationConfirm(BaseModel):
    """POST /auth/verify-email body."""
    token: str


class ResendVerificationRequest(BaseModel):
    """POST /auth/resend-verification body."""
    email: EmailStr
