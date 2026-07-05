"""
User profile, preferences, and avatar schemas.
"""
from typing import Any

from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    """PATCH /users/me body. Every field optional — only supplied fields
    are updated (partial update semantics)."""
    full_name: str | None = Field(default=None, min_length=1, max_length=255)


class UserPreferences(BaseModel):
    """
    Free-form but typed-where-known preferences. Deliberately permissive
    (`extra="allow"`) so a future challenge-specific preference can be
    added by the frontend without requiring a backend schema change —
    while the fields listed here get real validation and IDE support for
    the common cases every app tends to need.
    """
    model_config = {"extra": "allow"}

    theme: str | None = Field(default=None, pattern="^(light|dark|system)$")
    language: str | None = Field(default=None, min_length=2, max_length=10)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    notifications_enabled: bool | None = None


class UserPreferencesResponse(BaseModel):
    preferences: dict[str, Any]


class AvatarUploadResponse(BaseModel):
    avatar_url: str
