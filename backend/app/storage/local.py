import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.storage.base import ScreenshotStorage, StoredScreenshotMetadata


class LocalScreenshotStorage(ScreenshotStorage):
    """Local filesystem screenshot storage isolated from application source code.
    Enforces strict path-traversal immunity and generates server-side nonces for filenames.
    """

    def __init__(self, base_dir: Optional[str] = None):
        # Resolve absolute base directory
        if base_dir:
            self.base_path = Path(base_dir).resolve()
        else:
            # Default to settings.SCREENSHOT_STORAGE_DIR relative to project root
            self.base_path = Path(settings.SCREENSHOT_STORAGE_DIR).resolve()

        # Ensure isolated storage directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, storage_key: str) -> Path:
        """Resolves a storage key to a filesystem path, strictly verifying directory containment."""
        # Sanitize key to prevent path traversal
        clean_key = os.path.basename(storage_key)
        target_path = (self.base_path / clean_key).resolve()

        # Path traversal guard: must be strictly inside base_path
        try:
            target_path.relative_to(self.base_path)
        except ValueError:
            raise ValueError(f"Security error: storage path traversal attempt detected for key '{storage_key}'.")

        return target_path

    async def save(
        self,
        file_bytes: bytes,
        extension: str,
        mime_type: str,
        sha256_hash: str,
    ) -> StoredScreenshotMetadata:
        """Saves image bytes into isolated storage using a server-generated UUID."""
        # Ensure extension starts with a dot and is clean
        clean_ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        
        # Server-side generated random UUID nonce — user filename is NEVER used
        nonce = uuid.uuid4().hex
        storage_key = f"{nonce}{clean_ext}"
        target_path = self._resolve_safe_path(storage_key)

        # Write file atomically/safely
        with open(target_path, "wb") as f:
            f.write(file_bytes)

        return StoredScreenshotMetadata(
            storage_key=storage_key,
            file_path=str(target_path),
            file_size_bytes=len(file_bytes),
            sha256_hash=sha256_hash,
            mime_type=mime_type,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    async def get(self, storage_key: str) -> Optional[bytes]:
        """Retrieves file bytes for a verified storage key."""
        target_path = self._resolve_safe_path(storage_key)
        if not target_path.is_file():
            return None
        with open(target_path, "rb") as f:
            return f.read()

    async def delete(self, storage_key: str) -> bool:
        """Deletes a stored file if it exists."""
        target_path = self._resolve_safe_path(storage_key)
        if target_path.is_file():
            target_path.unlink()
            return True
        return False
