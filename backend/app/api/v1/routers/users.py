"""
User profile router. HTTP concerns only — validation via Pydantic,
delegation to UserService for everything else.
"""
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_user_repository
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRead
from app.schemas.user import (
    AvatarUploadResponse,
    UserPreferences,
    UserPreferencesResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current user's profile",
    description="Alias of /auth/me, provided under /users for REST-conventional grouping of profile endpoints.",
)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update the current user's profile",
    description="Partial update — only supplied fields are changed. Currently supports `full_name`.",
    responses={200: {"description": "Profile updated."}, 401: {"description": "Not authenticated."}},
)
async def update_my_profile(
    payload: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    updated = await service.update_profile(current_user, payload.full_name)
    await db.commit()
    return UserRead.model_validate(updated)


@router.get(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    summary="Get the current user's preferences",
    description="Returns the free-form preferences JSON blob (theme, language, currency, notification settings, etc.).",
)
async def get_my_preferences(current_user: User = Depends(get_current_user)) -> UserPreferencesResponse:
    return UserPreferencesResponse(preferences=current_user.preferences or {})


@router.put(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    summary="Update the current user's preferences",
    description=(
        "Shallow-merges the supplied fields into existing preferences — "
        "omitted fields are left unchanged, not cleared. Accepts arbitrary "
        "additional keys beyond the typed ones (theme/language/currency/"
        "notifications_enabled) via `extra=allow`, so a future challenge-"
        "specific preference doesn't require a backend schema change."
    ),
    responses={200: {"description": "Preferences updated."}, 401: {"description": "Not authenticated."}},
)
async def update_my_preferences(
    payload: UserPreferences,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPreferencesResponse:
    updated = await service.update_preferences(current_user, payload.model_dump(exclude_unset=True))
    await db.commit()
    return UserPreferencesResponse(preferences=updated)


@router.post(
    "/me/avatar",
    response_model=AvatarUploadResponse,
    summary="Upload a profile avatar",
    description=(
        "Multipart file upload. Accepts JPEG, PNG, or WebP only "
        "(validated by content-type, not by trusting the filename), up to "
        "AVATAR_MAX_SIZE_MB (default 5MB). The server generates the stored "
        "filename itself — the client-supplied filename is never used for "
        "anything, eliminating path-traversal/filename-injection risk. "
        "Replaces and deletes any previous avatar for this user."
    ),
    responses={
        200: {"description": "Avatar uploaded."},
        401: {"description": "Not authenticated."},
        422: {"description": "Unsupported file type or file too large."},
    },
)
async def upload_my_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> AvatarUploadResponse:
    avatar_url = await service.save_avatar(current_user, file)
    await db.commit()
    return AvatarUploadResponse(avatar_url=avatar_url)
