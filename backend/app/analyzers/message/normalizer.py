import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from app.analyzers.url.normalizer import defang_url


@dataclass(frozen=True)
class NormalizedMessage:
    """Immutable representation of a normalized message for deterministic analysis and persistence."""
    raw_content: str
    normalized_content: str
    defanged_content: str
    subject: Optional[str]
    sender: Optional[str]
    sender_metadata: Optional[str]
    content_hash: str
    char_count: int
    line_count: int


def defang_message_text(text: str) -> str:
    """Safely defangs URLs and dots in message content for safe UI presentation and logging.
    
    Transforms:
        http:// -> hxxp://
        https:// -> hxxps://
        . -> [.] inside domains
    """
    if not text:
        return ""

    def replace_url_match(match: re.Match) -> str:
        return defang_url(match.group(0))

    # Match URLs with schemes or www prefix
    url_pattern = re.compile(r"(?:https?|hxxps?|ftp)://[^\s<>\"']+|www\.[^\s<>\"']+", re.IGNORECASE)
    defanged = url_pattern.sub(replace_url_match, text)

    # Defang suspicious bare dot patterns that look like domains (e.g. evil[.]com)
    defanged = re.sub(r"([a-zA-Z0-9_-]+)\.([a-zA-Z]{2,6}\b)", r"\1[.]\2", defanged)
    return defanged


def normalize_message(
    content: str,
    subject: Optional[str] = None,
    sender: Optional[str] = None,
    sender_metadata: Optional[str] = None,
) -> NormalizedMessage:
    """Safely normalizes untrusted message text without executing any code.
    
    Operations:
    1. Unicode normalization (NFKC) to resolve homoglyphs and compatibility characters.
    2. Line endings standardization to unix newline (\n).
    3. Normalizes excessive whitespace and tabs while preserving paragraph boundaries.
    4. Strips dangerous unprintable / null control characters (except \n, \t).
    5. Normalizes optional metadata (subject, sender, sender_metadata).
    6. Produces defanged text and deterministic SHA-256 hash.
    """
    if not content or not content.strip():
        raise ValueError("Message content cannot be empty")

    raw_text = content

    # 1. Unicode NFKC normalization
    normalized_text = unicodedata.normalize("NFKC", raw_text)

    # 2. Strip null bytes and non-printable control characters (keep \t and \n)
    normalized_text = "".join(ch for ch in normalized_text if ch in ("\t", "\n") or (ord(ch) >= 32 and ord(ch) != 127))

    # 3. Standardize line endings (\r\n and \r -> \n)
    normalized_text = normalized_text.replace("\r\n", "\n").replace("\r", "\n")

    # 4. Collapse 3+ consecutive line breaks into 2, and trim trailing whitespace per line
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized_text.split("\n")]
    normalized_text = "\n".join(lines)
    normalized_text = re.sub(r"\n{3,}", "\n\n", normalized_text).strip()

    # 5. Metadata normalization
    norm_subject = unicodedata.normalize("NFKC", subject.strip()) if subject and subject.strip() else None
    norm_sender = unicodedata.normalize("NFKC", sender.strip()) if sender and sender.strip() else None
    norm_sender_meta = unicodedata.normalize("NFKC", sender_metadata.strip()) if sender_metadata and sender_metadata.strip() else None

    # 6. Defanged representation
    defanged_text = defang_message_text(normalized_text)

    # 7. Compute deterministic SHA-256 hash of normalized content + subject
    hash_payload = f"{norm_subject or ''}\n{normalized_text}"
    content_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

    return NormalizedMessage(
        raw_content=raw_text,
        normalized_content=normalized_text,
        defanged_content=defanged_text,
        subject=norm_subject,
        sender=norm_sender,
        sender_metadata=norm_sender_meta,
        content_hash=content_hash,
        char_count=len(normalized_text),
        line_count=len(lines),
    )
