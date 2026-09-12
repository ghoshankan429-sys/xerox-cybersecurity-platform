import hashlib
import os
import struct
from dataclasses import dataclass
from typing import Optional, Tuple
from app.core.config import settings


class ImageValidationError(ValueError):
    """Raised when an uploaded screenshot fails validation checks."""
    pass


@dataclass(frozen=True)
class ValidatedImage:
    """Result of successful screenshot validation."""
    content: bytes
    sha256_hash: str
    file_size_bytes: int
    mime_type: str
    safe_extension: str
    width: int
    height: int
    client_filename: str


class ScreenshotValidator:
    """Validates untrusted screenshot uploads against strict security constraints:
    - Maximum file size (10 MB) & zero-byte rejection
    - MIME type whitelist (PNG, JPEG, WEBP)
    - Cryptographic signature / magic-byte verification
    - Image dimension limits (max 4096 x 4096)
    - Pure header inspection with zero decompression or script execution
    """

    MAGIC_PNG = b"\x89PNG\r\n\x1a\n"
    MAGIC_JPEG = b"\xff\xd8\xff"
    MAGIC_RIFF = b"RIFF"
    MAGIC_WEBP = b"WEBP"

    @classmethod
    def validate(
        cls,
        file_bytes: bytes,
        declared_mime: Optional[str] = None,
        client_filename: Optional[str] = None,
    ) -> ValidatedImage:
        """Validates screenshot bytes, enforces security rules, and extracts dimensions."""
        file_size = len(file_bytes)

        # 1. Size Constraints
        if file_size == 0:
            raise ImageValidationError("Uploaded image file is empty (0 bytes).")
        if file_size > settings.MAX_SCREENSHOT_SIZE_BYTES:
            max_mb = settings.MAX_SCREENSHOT_SIZE_BYTES / (1024 * 1024)
            raise ImageValidationError(f"File size exceeds maximum allowed limit of {max_mb:.0f} MB.")

        # 2. Magic Bytes Verification & Format Detection
        detected_format, safe_ext, actual_mime = cls._detect_format(file_bytes)
        if not detected_format:
            raise ImageValidationError("Unsupported or invalid image file signature. Only PNG, JPEG, and WEBP are accepted.")

        # 3. MIME Alignment Check
        if declared_mime:
            clean_declared = declared_mime.lower().split(";")[0].strip()
            # Normalize jpg/jpeg
            if clean_declared == "image/jpg":
                clean_declared = "image/jpeg"
            if clean_declared != actual_mime:
                raise ImageValidationError(
                    f"MIME type mismatch: declared '{declared_mime}' does not match verified signature '{actual_mime}'."
                )

        # 4. Dimension Extraction via Pure Header Inspection
        width, height = cls._extract_dimensions(file_bytes, detected_format)
        if width <= 0 or height <= 0:
            raise ImageValidationError("Malformed image header: invalid dimensions.")
        if width > settings.MAX_IMAGE_WIDTH or height > settings.MAX_IMAGE_HEIGHT:
            raise ImageValidationError(
                f"Image dimensions ({width}x{height}) exceed maximum allowed {settings.MAX_IMAGE_WIDTH}x{settings.MAX_IMAGE_HEIGHT}px."
            )

        # 5. Sanitize client-provided filename for audit logging only
        safe_client_name = "screenshot"
        if client_filename:
            # Strip directories and null bytes
            base = os.path.basename(client_filename).replace("\x00", "").strip()
            if base:
                safe_client_name = base[:128]

        # 6. Compute SHA-256 Hash
        sha256 = hashlib.sha256(file_bytes).hexdigest()

        return ValidatedImage(
            content=file_bytes,
            sha256_hash=sha256,
            file_size_bytes=file_size,
            mime_type=actual_mime,
            safe_extension=safe_ext,
            width=width,
            height=height,
            client_filename=safe_client_name,
        )

    @classmethod
    def _detect_format(cls, data: bytes) -> Tuple[Optional[str], str, str]:
        """Inspects leading magic bytes to identify image format."""
        if len(data) >= 8 and data[:8] == cls.MAGIC_PNG:
            return "PNG", ".png", "image/png"
        if len(data) >= 3 and data[:3] == cls.MAGIC_JPEG:
            return "JPEG", ".jpg", "image/jpeg"
        if len(data) >= 12 and data[:4] == cls.MAGIC_RIFF and data[8:12] == cls.MAGIC_WEBP:
            return "WEBP", ".webp", "image/webp"
        return None, "", ""

    @classmethod
    def _extract_dimensions(cls, data: bytes, fmt: str) -> Tuple[int, int]:
        """Extracts (width, height) purely from file headers without decompressing pixel data."""
        try:
            if fmt == "PNG":
                # PNG IHDR chunk starts at byte 12: 4 bytes length, 4 bytes 'IHDR', 4 bytes width, 4 bytes height
                if len(data) >= 24 and data[12:16] == b"IHDR":
                    w, h = struct.unpack(">II", data[16:24])
                    return w, h
                raise ImageValidationError("Malformed PNG: missing or corrupt IHDR chunk.")

            elif fmt == "JPEG":
                # JPEG markers scan
                offset = 2
                length = len(data)
                while offset < length:
                    if data[offset] != 0xFF:
                        offset += 1
                        continue
                    marker = data[offset + 1]
                    # Start of Frame markers: SOF0 to SOF3, SOF5 to SOF7, SOF9 to SOF11, SOF13 to SOF15
                    if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        # SOF header: marker(2), len(2), precision(1), height(2), width(2)
                        if offset + 9 <= length:
                            h, w = struct.unpack(">HH", data[offset + 5:offset + 9])
                            return w, h
                        break
                    elif marker in (0xD9, 0xDA):  # EOI or SOS (start of scan)
                        break
                    else:
                        # Skip variable-length marker
                        if offset + 4 <= length:
                            marker_len = struct.unpack(">H", data[offset + 2:offset + 4])[0]
                            offset += 2 + marker_len
                        else:
                            break
                raise ImageValidationError("Malformed JPEG: SOF frame marker not found.")

            elif fmt == "WEBP":
                # WEBP formats: VP8 (lossy), VP8L (lossless), VP8X (extended)
                if len(data) >= 30:
                    chunk_type = data[12:16]
                    if chunk_type == b"VP8 ":
                        # Lossy VP8: keyframe header at offset 23..29
                        # 3 bytes start code 0x9d 0x01 0x2a
                        if data[23:26] == b"\x9d\x01\x2a":
                            w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
                            h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
                            return w, h
                    elif chunk_type == b"VP8L":
                        # Lossless VP8L: signature 0x2f at offset 21
                        if data[20] == 0x2F:
                            b0, b1, b2, b3 = data[21:25]
                            w = 1 + (((b1 & 0x3F) << 8) | b0)
                            h = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
                            return w, h
                    elif chunk_type == b"VP8X":
                        # Extended VP8X: canvas width 3 bytes at 24..27, height 3 bytes at 27..30
                        w = 1 + (data[24] | (data[25] << 8) | (data[26] << 16))
                        h = 1 + (data[27] | (data[28] << 8) | (data[29] << 16))
                        return w, h
                raise ImageValidationError("Malformed WEBP: unrecognizable chunk headers.")

        except Exception as exc:
            if isinstance(exc, ImageValidationError):
                raise
            raise ImageValidationError(f"Could not parse image header: {str(exc)}")

        raise ImageValidationError(f"Could not determine dimensions for {fmt} image.")
