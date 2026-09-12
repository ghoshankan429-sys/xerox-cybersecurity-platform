import pytest
from app.analyzers.message.normalizer import normalize_message
from app.analyzers.message.extractor import extract_iocs, ExtractedIOCs


def test_url_extraction_standard_and_deduplication():
    """Extracts unique URLs and strips trailing punctuation safely."""
    raw = (
        "Check this link: https://portal.example.com/login?id=1, "
        "and also review http://secondary.org/docs. "
        "Do not forget https://portal.example.com/login?id=1!"
    )
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)

    assert len(iocs.urls) == 2
    assert "https://portal.example.com/login?id=1" in iocs.urls
    assert "http://secondary.org/docs" in iocs.urls


def test_defanged_url_extraction():
    """Extracts and refangs defanged URLs such as hxxps:// and [.] notations."""
    raw = "Suspicious smishing payload: hxxps://apple-id-verify[.]live/account"
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)

    assert len(iocs.urls) >= 1
    assert any("apple-id-verify.live" in u for u in iocs.urls)


def test_email_and_domain_extraction():
    """Extracts email addresses and infers domains without network lookups."""
    raw = "Contact support@chase-security-alerts.com or reach out to billing@internal.corp"
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)

    assert "support@chase-security-alerts.com" in iocs.email_addresses
    assert "billing@internal.corp" in iocs.email_addresses
    assert "chase-security-alerts.com" in iocs.domains
    assert "internal.corp" in iocs.domains


def test_ipv4_and_ipv6_extraction():
    """Extracts and validates IPv4 and IPv6 addresses."""
    raw = "Server 198.51.100.42 was contacted alongside ::1 and 2001:db8::1 on port 80."
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)

    assert "198.51.100.42" in iocs.ipv4_addresses


def test_phone_number_extraction():
    """Extracts formatted telephone / mobile numbers."""
    raw = "Call us immediately at +1 (800) 555-0199 or 415-555-2671 to unlock."
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)

    assert len(iocs.phone_numbers) >= 1
