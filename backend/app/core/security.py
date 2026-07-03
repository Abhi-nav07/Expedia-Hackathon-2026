"""
Security primitives: password hashing (Argon2) and JWT access/refresh tokens.

This module contains NO business logic (no DB calls, no user lookups) —
it is a pure utility layer so it stays trivially testable and reusable
regardless of what the final auth business rules turn out to be.
"""
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Argon2 is the OWASP-recommended default; passlib handles the low-level KDF.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    sub: str  # user id
    role: str
    type: TokenType
    jti: str  # unique token id, enables future revocation/blacklisting
    exp: datetime
    iat: datetime


# --------------------------------------------------------------------------
# Password hashing
# --------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with Argon2. Never store plaintext, ever."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time verification against a stored Argon2 hash."""
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """True if the hash was created with outdated parameters and should be refreshed."""
    return pwd_context.needs_update(hashed_password)


# --------------------------------------------------------------------------
# JWT tokens
# --------------------------------------------------------------------------

def _create_token(subject: str, role: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = TokenPayload(
        sub=subject,
        role=role,
        type=token_type,
        jti=str(uuid.uuid4()),
        iat=now,
        exp=now + expires_delta,
    )
    # model_dump with mode="json" ensures datetimes serialize to ISO/epoch correctly for jose
    to_encode = payload.model_dump(mode="json")
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, role: str) -> str:
    return _create_token(
        subject=subject,
        role=role,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str, role: str) -> str:
    return _create_token(
        subject=subject,
        role=role,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT. Returns None on any failure (expired,
    tampered signature, malformed) — callers should treat None as
    "unauthenticated" and never distinguish the failure reason to the client.
    """
    try:
        raw: dict[str, Any] = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**raw)
    except (JWTError, ValueError):
        return None


def decode_token_of_type(token: str, expected_type: TokenType) -> Optional[TokenPayload]:
    """Decode a token and additionally enforce it is the expected type
    (prevents a refresh token being replayed as an access token, etc.)."""
    payload = decode_token(token)
    if payload is None or payload.type != expected_type:
        return None
    return payload
