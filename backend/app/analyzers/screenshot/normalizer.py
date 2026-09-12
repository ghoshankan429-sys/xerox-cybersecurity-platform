import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedOCR:
    """Normalized OCR text payload with defanged representations for safe display."""
    raw_text: str
    normalized_text: str
    defanged_text: str
    char_count: int
    line_count: int


def normalize_ocr_text(raw_text: str) -> NormalizedOCR:
    """Normalizes raw OCR/vision output text by:
    - Normalizing Unicode NFKC to resolve lookalike characters
    - Converting CRLF and CR to standard LF newlines
    - Stripping null bytes and dangerous control characters
    - Repairing common OCR spacing artifacts in URLs and domains
    """
    if not raw_text:
        return NormalizedOCR(
            raw_text="",
            normalized_text="",
            defanged_text="",
            char_count=0,
            line_count=0,
        )

    # 1. Strip null bytes
    cleaned = raw_text.replace("\x00", "")

    # 2. Unicode NFKC normalization
    cleaned = unicodedata.normalize("NFKC", cleaned)

    # 3. Standardize newlines
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    # 4. Filter unprintable control characters (preserve \n and \t)
    cleaned = "".join(ch for ch in cleaned if ch in ("\n", "\t") or unicodedata.category(ch)[0] != "C")

    # 5. Fix common OCR URL spacing artifacts (e.g., "http : //" -> "http://", "https : / /" -> "https://")
    cleaned = re.sub(r"\b(https?)\s*:\s*/\s*/\s*", r"\1://", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(hxxps?)\s*:\s*/\s*/\s*", r"\1://", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[\s*\.\s*\]", "[.]", cleaned)
    cleaned = re.sub(r"\(\s*\.\s*\)", "(.)", cleaned)

    # 6. Build defanged version for UI display
    defanged = defang_ocr_text(cleaned)

    lines = cleaned.split("\n")
    return NormalizedOCR(
        raw_text=raw_text,
        normalized_text=cleaned,
        defanged_text=defanged,
        char_count=len(cleaned),
        line_count=len(lines),
    )


def defang_ocr_text(text: str) -> str:
    """Defangs URLs, schemes, and domains in OCR text to prevent accidental client execution."""
    if not text:
        return ""
    # Defang scheme
    out = re.sub(r"https://", "hxxps://", text, flags=re.IGNORECASE)
    out = re.sub(r"http://", "hxxp://", out, flags=re.IGNORECASE)
    # Defang common domain indicators if not already defanged
    out = re.sub(r"(?<!\[)\.(?!\s*\])", "[.]", out)
    return out
