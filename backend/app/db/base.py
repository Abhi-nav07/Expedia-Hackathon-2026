"""
Declarative base and reusable model mixins.

Every ORM model in the platform should inherit from Base and, where
applicable, the mixins below — this keeps timestamp/soft-delete/PK
conventions consistent across every future table without repeating code.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Root declarative base — all models inherit from this."""
    pass


class UUIDPrimaryKeyMixin:
    """UUID primary keys instead of sequential ints: avoids enumeration
    attacks on public-facing resource IDs (e.g. /bookings/1, /bookings/2)."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """created_at / updated_at, always UTC, always server-independent."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Soft delete: rows are flagged, never physically removed, so nothing
    referencing them (bookings, reviews, audit logs) breaks or loses history."""
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
