"""
Unit tests for app.core.permissions. Not yet wired into any live
endpoint (see permissions.py's docstring — it's infrastructure ahead of
a concrete consumer), but the role->permission mapping logic is real and
should be verified now rather than shipped with 0% coverage.
"""
from app.core.permissions import ALL_PERMISSIONS, Permission, role_has_permission
from app.models.user import UserRole


def test_admin_has_every_permission_via_wildcard():
    assert role_has_permission(UserRole.ADMIN, Permission.USERS_READ) is True
    assert role_has_permission(UserRole.ADMIN, Permission.USERS_WRITE) is True
    assert role_has_permission(UserRole.ADMIN, Permission.ADMIN_FULL) is True
    assert role_has_permission(UserRole.ADMIN, "some:future:permission:not:yet:defined") is True


def test_regular_user_has_only_granted_permissions():
    assert role_has_permission(UserRole.USER, Permission.USERS_READ) is True
    assert role_has_permission(UserRole.USER, Permission.USERS_WRITE) is True
    assert role_has_permission(UserRole.USER, Permission.USERS_READ_ALL) is False
    assert role_has_permission(UserRole.USER, Permission.ADMIN_FULL) is False


def test_partner_has_same_base_permissions_as_user():
    assert role_has_permission(UserRole.PARTNER, Permission.USERS_READ) is True
    assert role_has_permission(UserRole.PARTNER, Permission.ADMIN_FULL) is False


def test_all_permissions_wildcard_is_not_a_real_permission_string():
    """Sanity check that the wildcard sentinel isn't accidentally treated
    as a grantable permission for non-admin roles."""
    assert role_has_permission(UserRole.USER, ALL_PERMISSIONS) is False
