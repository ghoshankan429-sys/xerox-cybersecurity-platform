import pytest
from app.analyzers.message.normalizer import (
    normalize_message,
    defang_message_text,
    NormalizedMessage,
)


def test_unicode_nfkc_normalization():
    """Full-width characters and compatibility glyphs are normalized to standard ASCII/Unicode."""
    # Full-width "Ｈｅｌｌｏ Ｗｏｒｌｄ"
    full_width = "Ｈｅｌｌｏ Ｗｏｒｌｄ: ｖｅｒｉｆｙ ｙｏｕｒ ａｃｃｏｕｎｔ"
    norm = normalize_message(full_width)
    assert norm.normalized_content == "Hello World: verify your account"


def test_whitespace_and_newline_standardization():
    """Multi-line messages with Windows \r\n and ragged indentation are cleanly standardized."""
    raw = "Line 1\r\n\r\n   Line 2   \r\n\r\n\r\n\r\nLine 3   \t   "
    norm = normalize_message(raw)
    assert "\r" not in norm.normalized_content
    assert "Line 1\n\nLine 2\n\nLine 3" == norm.normalized_content


def test_null_byte_and_control_character_removal():
    """Dangerous null bytes and non-printable control characters are stripped."""
    raw = "Clean\x00Message\x08With\x1fControl\nCharacters"
    norm = normalize_message(raw)
    assert "\x00" not in norm.normalized_content
    assert "\x08" not in norm.normalized_content
    assert "\x1f" not in norm.normalized_content
    assert "CleanMessageWithControl\nCharacters" == norm.normalized_content


def test_defang_message_text():
    """Embedded links in message text are defanged to prevent accidental clicking."""
    raw = "Click here: https://phishing-portal.xyz/login or http://malicious.com"
    defanged = defang_message_text(raw)
    assert "hxxps://" in defanged
    assert "hxxp://" in defanged
    assert "https://" not in defanged
    assert "http://" not in defanged


def test_sha256_content_hashing():
    """Identical logical messages produce identical SHA-256 content hashes."""
    msg1 = normalize_message("  Urgent security alert!  \r\n\r\nVerify now.  ", subject="Alert")
    msg2 = normalize_message("Urgent security alert!\n\nVerify now.", subject="Alert")
    assert msg1.content_hash == msg2.content_hash
    assert len(msg1.content_hash) == 64


def test_empty_content_rejection():
    """Empty or whitespace-only messages raise a ValueError."""
    with pytest.raises(ValueError):
        normalize_message("   \n\t   ")
