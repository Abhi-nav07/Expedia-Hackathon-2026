"""
Permission-based authorization.

Roles (app.models.user.UserRole) answer "what kind of account is this."
Permissions answer "what is this account allowed to do" — a finer-grained
layer on top, so future business features can gate on a specific
capability (e.g. "bookings:write") rather than hardcoding role checks
scattered through routers. Adding a new permission or role later means
editing ROLE_PERMISSIONS in one place.

This is intentionally an in-code mapping, not a database table — a
DB-backed permission system is real infrastructure but is only worth the
complexity once there's an actual admin UI to manage it; that's a
reasonable future upgrade, not a gap being hidden here.
"""
from fastapi import Depends

from app.api.v1.deps import get_current_user
from app.core.exceptions import ForbiddenException
from app.models.user import User, UserRole

# Wildcard meaning "every permission" — used only for admin.
ALL_PERMISSIONS = "*"


class Permission:
    """String constants rather than an Enum, so future modules can add
    new permission strings without editing this file (just reference the
    string) — while these constants give autocomplete + a canonical list
    for anything defined so far."""

    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_READ_ALL = "users:read:all"  # read other users' data (admin)
    ADMIN_FULL = "admin:full"


ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.USER: {Permission.USERS_READ, Permission.USERS_WRITE},
    UserRole.PARTNER: {Permission.USERS_READ, Permission.USERS_WRITE},
    UserRole.ADMIN: {ALL_PERMISSIONS},
}


def role_has_permission(role: UserRole, permission: str) -> bool:
    granted = ROLE_PERMISSIONS.get(role, set())
    return ALL_PERMISSIONS in granted or permission in granted


def require_permission(permission: str):
    """
    Dependency factory: use as
    `current_user: User = Depends(require_permission(Permission.USERS_READ_ALL))`
    on any route that needs to gate on a specific capability rather than
    a whole role.
    """

    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if not role_has_permission(current_user.role, permission):
            raise ForbiddenException("You do not have permission to perform this action")
        return current_user

    return _guard
