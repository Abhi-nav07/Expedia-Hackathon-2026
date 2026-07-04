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
