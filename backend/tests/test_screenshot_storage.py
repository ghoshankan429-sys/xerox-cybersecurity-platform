import pytest
import shutil
import tempfile
from pathlib import Path
from app.storage.local import LocalScreenshotStorage


@pytest.fixture
def temp_storage():
    tmp_dir = tempfile.mkdtemp(prefix="xerox_test_storage_")
    storage = LocalScreenshotStorage(base_dir=tmp_dir)
    yield storage
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_save_and_retrieve_screenshot(temp_storage):
    sample_data = b"XEROX_TEST_IMAGE_DATA_12345"
    meta = await temp_storage.save(
        file_bytes=sample_data,
        extension=".png",
        mime_type="image/png",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )

    assert meta.storage_key.endswith(".png")
    assert meta.file_size_bytes == len(sample_data)
    assert Path(meta.file_path).exists()

    # Retrieve
    retrieved = await temp_storage.get(meta.storage_key)
    assert retrieved == sample_data


@pytest.mark.asyncio
async def test_delete_screenshot(temp_storage):
    sample_data = b"TEST_DELETE_PAYLOAD"
    meta = await temp_storage.save(
        file_bytes=sample_data,
        extension=".jpg",
        mime_type="image/jpeg",
        sha256_hash="abcd",
    )
    assert Path(meta.file_path).exists()

    # Delete
    deleted = await temp_storage.delete(meta.storage_key)
    assert deleted is True
    assert not Path(meta.file_path).exists()

    # Second delete returns False
    deleted_again = await temp_storage.delete(meta.storage_key)
    assert deleted_again is False


@pytest.mark.asyncio
async def test_path_traversal_protection(temp_storage):
    # Attempting to access parent directories via storage key
    traversal_key = "../../etc/passwd"
    # LocalScreenshotStorage._resolve_safe_path applies basename which neutralizes slashes,
    # and if resolved outside base_dir raises ValueError.
    target = temp_storage._resolve_safe_path(traversal_key)
    # The resolved file must be inside the base directory
    assert target.parent == temp_storage.base_path
