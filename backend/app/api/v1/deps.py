"""
Shared FastAPI dependencies for the v1 API: DB-scoped repositories/services,
current-user resolution from a Bearer token, and RBAC guards.
"""
import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import TokenType, decode_token_of_type
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    if credentials is None:
        raise UnauthorizedException("Authentication required")

    payload = decode_token_of_type(credentials.credentials, TokenType.ACCESS)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    try:
        user_id = uuid.UUID(payload.sub)
    except ValueError:
        raise UnauthorizedException("Invalid token subject")

    user = await repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedException("Account is inactive or no longer exists")

    return user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for RBAC: use as
    `current_user: User = Depends(require_role(UserRole.ADMIN))`
    on any route that needs to restrict access by role.
    """

    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException("You do not have permission to perform this action")
        return current_user

    return _guard


# Convenience pre-built guards for the most common cases
require_admin = require_role(UserRole.ADMIN)
require_any_authenticated_user = get_current_user
