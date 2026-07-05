"""
User model.

Deliberately generic — no travel-domain fields (no "loyalty_tier",
"preferred_airport", etc.) since the challenge domain isn't known yet.
Add domain-specific fields via a separate related table later rather
than growing this one, to keep auth concerns isolated.

Portability note: role uses native_enum=False so it's stored as a
VARCHAR + CHECK constraint on every backend (SQLite, PostgreSQL,
Supabase) rather than PostgreSQL's native CREATE TYPE enum, which
SQLite has no equivalent for. The primary key uses UUIDPrimaryKeyMixin
(backed by app.db.types.GUID), portable the same way.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    PARTNER = "partner"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.USER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Account lockout tracking (brute-force protection)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped["datetime | None"] = mapped_column(DateTime(timezone=True), nullable=True)

    # Profile / settings — deliberately generic (no travel-domain fields).
    # preferences is a free-form JSON blob (TEXT on SQLite, JSONB on
    # PostgreSQL/Supabase — see docs/05-database-portability.md) rather
    # than a rigid column-per-setting schema, so adding a new preference
    # later doesn't require a migration.
    avatar_url: Mapped["str | None"] = mapped_column(String(512), nullable=True)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email} role={self.role}>"
