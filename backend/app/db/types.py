"""
Database-portable column types.

This module exists so that exactly ONE place in the codebase knows how
UUIDs are physically stored, regardless of database backend. Everything
else (models, repositories, services, schemas) works with plain Python
uuid.UUID objects and never needs to know or care whether the underlying
DB is SQLite, PostgreSQL, or Supabase.

Design choice: GUID always stores a CHAR(36) hyphenated string, on every
dialect — including PostgreSQL/Supabase. This is deliberate, not a
missed optimization: the Alembic migration (0001_create_users_table.py)
creates a plain CHAR(36) column identically on every backend, with no
dialect-specific branching. If GUID instead mapped to PostgreSQL's native
UUID type at the ORM level, it would silently mismatch the actual column
type created by the migration on a fresh Postgres/Supabase deploy —
reads would fail. Keeping GUID's Python-level behavior and the
migration's DDL in lockstep (both always CHAR(36)) is what makes the
SQLite -> PostgreSQL/Supabase swap actually safe with zero code changes,
at the minor cost of not using Postgres' native UUID indexing.
"""
import uuid
from datetime import timezone

from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent UUID type — always physically stored as
    CHAR(36) (the canonical hyphenated string form), on every dialect."""

    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(str(value)))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


def ensure_utc(dt):
    """
    Normalizes a datetime loaded from the DB to be timezone-aware (UTC).

    Cross-dialect gotcha: PostgreSQL/Supabase preserve tzinfo on a
    `DateTime(timezone=True)` column round-trip; SQLite does NOT — it
    silently returns a naive datetime even though the column was declared
    timezone-aware. Every value this app ever writes to such a column is
    already UTC (see TimestampMixin, User.locked_until), so a naive value
    read back can be safely assumed to be UTC and re-attached with
    tzinfo. Without this, comparing a SQLite-loaded datetime against
    `datetime.now(timezone.utc)` raises `TypeError: can't compare
    offset-naive and offset-aware datetimes` — caught the hard way, by
    actually running the account-lockout code path (see Module 10 notes)
    rather than by reasoning about SQLite's behavior in advance.

    Use this any time a stored datetime is compared against a
    timezone-aware `datetime.now(timezone.utc)`.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
