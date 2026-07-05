"""
User profile service — profile updates, preferences, and avatar upload.

Kept separate from AuthService: this is profile/settings management, not
identity/session management. Same separation-of-concerns reasoning as
schemas/user.py vs schemas/auth.py.
"""
import uuid
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationException
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = get_logger("user_service")

# Whitelist by content-type, not by trusting the client-supplied filename
# or extension — file security requirement: never trust client input for
# anything that touches the filesystem.
ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def update_profile(self, user: User, full_name: str | None) -> User:
        if full_name is not None:
            user.full_name = full_name
        return await self.repo.save(user)

    async def get_preferences(self, user: User) -> dict[str, Any]:
        return user.preferences or {}

    async def update_preferences(self, user: User, updates: dict[str, Any]) -> dict[str, Any]:
        """
        Shallow-merges `updates` into the existing preferences blob rather
        than replacing it wholesale — so updating just `theme` doesn't
        silently wipe out `language`/`currency`/etc. that a different
        request set previously.
        """
        current = dict(user.preferences or {})
        current.update({k: v for k, v in updates.items() if v is not None})
        user.preferences = current
        await self.repo.save(user)
        return user.preferences

    async def save_avatar(self, user: User, file: UploadFile) -> str:
        """
        Validates and persists an avatar upload. Returns the new
        avatar_url. Validation, in order:
          1. Content-type whitelist (image/jpeg, image/png, image/webp only)
          2. Size limit (settings.AVATAR_MAX_SIZE_MB), enforced by reading
             in chunks and aborting early rather than trusting a
             Content-Length header (which the client controls and can lie
             about)
          3. Filename is NEVER taken from the client — we generate
             `{user_id}_{uuid}{ext}` ourselves, eliminating path traversal
             and filename-injection risk entirely.
        """
        content_type = file.content_type
        if content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
            raise ValidationException(
                "Unsupported file type. Allowed: JPEG, PNG, WebP.",
                details={"received_content_type": content_type},
            )

        max_bytes = settings.AVATAR_MAX_SIZE_MB * 1024 * 1024
        chunks: list[bytes] = []
        total_size = 0
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > max_bytes:
                raise ValidationException(
                    f"File too large. Maximum size is {settings.AVATAR_MAX_SIZE_MB}MB."
                )
            chunks.append(chunk)

        upload_dir = Path(settings.AVATAR_UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        extension = ALLOWED_AVATAR_CONTENT_TYPES[content_type]
        filename = f"{user.id}_{uuid.uuid4().hex[:8]}{extension}"
        file_path = upload_dir / filename

        # Remove any previous avatar file for this user before writing
        # the new one, so orphaned files don't accumulate on disk.
        if user.avatar_url:
            old_filename = user.avatar_url.rsplit("/", 1)[-1]
            old_path = upload_dir / old_filename
            if old_path.exists() and old_path.is_relative_to(upload_dir):
                old_path.unlink(missing_ok=True)

        with open(file_path, "wb") as f:
            f.write(b"".join(chunks))

        avatar_url = f"/uploads/avatars/{filename}"
        user.avatar_url = avatar_url
        await self.repo.save(user)
        logger.info("avatar_uploaded", user_id=str(user.id), size_bytes=total_size)
        return avatar_url
