from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StoredScreenshotMetadata:
    """Metadata representing an isolated, securely stored screenshot."""
    storage_key: str
    file_path: str
    file_size_bytes: int
    sha256_hash: str
    mime_type: str
    created_at: str


class ScreenshotStorage(ABC):
    """Abstract interface for isolated screenshot file storage."""

    @abstractmethod
    async def save(
        self,
        file_bytes: bytes,
        extension: str,
        mime_type: str,
        sha256_hash: str,
    ) -> StoredScreenshotMetadata:
        """Persists image bytes in isolated storage and returns metadata."""
        pass

    @abstractmethod
    async def get(self, storage_key: str) -> Optional[bytes]:
        """Retrieves image bytes by storage key. Returns None if not found."""
        pass

    @abstractmethod
    async def delete(self, storage_key: str) -> bool:
        """Deletes a stored screenshot by storage key. Returns True if deleted."""
        pass
