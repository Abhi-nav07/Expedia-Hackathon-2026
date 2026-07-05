"""add avatar_url and preferences to users

Revision ID: 0002_add_user_profile_fields
Revises: 0001_create_users_table
Create Date: 2026-07-04 00:00:00

Portable across SQLite and PostgreSQL/Supabase: sa.JSON renders as TEXT
on SQLite and JSONB on PostgreSQL automatically — no dialect branching
needed here, consistent with the rest of this migration history.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_add_user_profile_fields"
down_revision: Union[str, None] = "0001_create_users_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(length=512), nullable=True))
    op.add_column(
        "users",
        sa.Column("preferences", sa.JSON(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("users", "preferences")
    op.drop_column("users", "avatar_url")
