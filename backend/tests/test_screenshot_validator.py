import pytest
import struct
from app.analyzers.screenshot.validator import ScreenshotValidator, ImageValidationError


SAMPLE_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

SAMPLE_WEBP = b"RIFF\x1a\x00\x00\x00WEBPVP8L\x0e\x00\x00\x00/\x00\x00\x00\x00\x07\x00\x10\x01\x00\x00\x00\x00\x00"

SAMPLE_JPEG = (
    b"\xff\xd8"
    + struct.pack(">HHBHHB", 0xFFC0, 11, 8, 120, 160, 1)
    + b"\x01\x11\x00\xff\xd9"
)


def test_valid_png_validation():
    result = ScreenshotValidator.validate(SAMPLE_PNG, declared_mime="image/png", client_filename="test_screenshot.png")
    assert result.mime_type == "image/png"
    assert result.safe_extension == ".png"
    assert result.width == 1
    assert result.height == 1
    assert result.client_filename == "test_screenshot.png"
    assert len(result.sha256_hash) == 64


def test_valid_jpeg_validation():
    result = ScreenshotValidator.validate(SAMPLE_JPEG, declared_mime="image/jpeg", client_filename="photo.jpg")
    assert result.mime_type == "image/jpeg"
    assert result.safe_extension == ".jpg"
    assert result.width == 160
    assert result.height == 120
    assert result.client_filename == "photo.jpg"


def test_valid_webp_validation():
    result = ScreenshotValidator.validate(SAMPLE_WEBP, declared_mime="image/webp", client_filename="capture.webp")
    assert result.mime_type == "image/webp"
    assert result.safe_extension == ".webp"
    assert result.width == 1
    assert result.height == 1


def test_empty_file_rejected():
    with pytest.raises(ImageValidationError, match="empty"):
        ScreenshotValidator.validate(b"", declared_mime="image/png")


def test_oversized_file_rejected():
    oversized = b"\x89PNG\r\n\x1a\n" + b"\x00" * (10 * 1024 * 1024 + 1)
    with pytest.raises(ImageValidationError, match="exceeds maximum allowed"):
        ScreenshotValidator.validate(oversized, declared_mime="image/png")


def test_unsupported_signature_rejected():
    with pytest.raises(ImageValidationError, match="Unsupported or invalid image file signature"):
        ScreenshotValidator.validate(b"<html><body>Not an image</body></html>", declared_mime="text/html")


def test_mime_mismatch_rejected():
    with pytest.raises(ImageValidationError, match="MIME type mismatch"):
        # JPEG content declared as PNG
        ScreenshotValidator.validate(SAMPLE_JPEG, declared_mime="image/png")


def test_dimension_limits_enforced():
    # Construct a PNG header declaring 5000 x 5000 pixels (exceeding 4096 limit)
    oversized_dim_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        + struct.pack(">II", 5000, 5000)
        + b"\x08\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )
    with pytest.raises(ImageValidationError, match="exceed maximum allowed"):
        ScreenshotValidator.validate(oversized_dim_png, declared_mime="image/png")


def test_filename_sanitization():
    result = ScreenshotValidator.validate(
        SAMPLE_PNG,
        declared_mime="image/png",
        client_filename="../../etc/passwd\x00.png",
    )
    assert "/" not in result.client_filename
    assert "\\" not in result.client_filename
    assert "\x00" not in result.client_filename
