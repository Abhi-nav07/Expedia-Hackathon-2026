"""
Unit tests for app.core.security — pure functions, no DB or HTTP needed.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    decode_token_of_type,
    hash_password,
    verify_password,
)


def test_hash_password_produces_different_hash_each_time():
    """Argon2 includes a random salt — hashing the same password twice
    must never produce identical output."""
    h1 = hash_password("Sam3Password1")
    h2 = hash_password("Sam3Password1")
    assert h1 != h2


def test_verify_password_accepts_correct_and_rejects_incorrect():
    hashed = hash_password("CorrectHorse1")
    assert verify_password("CorrectHorse1", hashed) is True
    assert verify_password("WrongPassword1", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token(subject="user-123", role="user")
    payload = decode_token(token)
    assert payload is not None
    assert payload.sub == "user-123"
    assert payload.role == "user"
    assert payload.type == TokenType.ACCESS


def test_refresh_token_cannot_be_used_as_access_token():
    """decode_token_of_type must enforce the `type` claim — a refresh
    token presented where an access token is expected must be rejected."""
    refresh = create_refresh_token(subject="user-123", role="user")
    result = decode_token_of_type(refresh, TokenType.ACCESS)
    assert result is None

    # But it IS valid as a refresh token
    result_as_refresh = decode_token_of_type(refresh, TokenType.REFRESH)
    assert result_as_refresh is not None


def test_tampered_signature_is_rejected():
    token = create_access_token(subject="user-123", role="user")
    tampered = token[:-4] + "abcd"  # corrupt the signature portion
    assert decode_token(tampered) is None


def test_expired_token_is_rejected():
    """Manually construct an already-expired token (bypassing the normal
    create_access_token helper, which always uses a future expiry) to
    verify decode_token actually enforces exp rather than only checking
    the signature."""
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "user-123",
        "role": "user",
        "type": TokenType.ACCESS.value,
        "jti": "test-jti",
        "iat": (now - timedelta(hours=1)).isoformat(),
        "exp": (now - timedelta(minutes=1)).isoformat(),
    }
    expired_token = jwt.encode(
        expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    assert decode_token(expired_token) is None


def test_malformed_token_is_rejected():
    assert decode_token("not-a-real-jwt") is None
