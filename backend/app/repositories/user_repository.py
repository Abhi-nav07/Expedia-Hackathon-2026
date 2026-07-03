"""
User repository — the only place in the codebase allowed to write
SQLAlchemy queries against the users table. Services call this layer;
they never touch the ORM/session directly.
"""
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email.lower(), User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def create(self, *, email: str, hashed_password: str, full_name: str) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def save(self, user: User) -> User:
        """Persist mutations made to an already-loaded User instance."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
