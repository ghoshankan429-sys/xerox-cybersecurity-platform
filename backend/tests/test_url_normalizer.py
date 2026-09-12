import pytest
from app.analyzers.url.normalizer import (
    normalize_url,
    defang_url,
    refang_url,
    NormalizedURL,
)


def test_refang_url_variants():
    """Verify refanging handles standard cybersecurity defanging notations."""
    assert refang_url("hxxps://malicious[.]com/login") == "https://malicious.com/login"
    assert refang_url("hxxp://evil(.)net/payload") == "http://evil.net/payload"
    assert refang_url("hxxps://target{.}org") == "https://target.org"
    assert refang_url("hxxps[colon]//evil[slash]path") == "https://evil/path"


def test_defang_url():
    """Verify defanging prevents accidental clicks in analyst UI."""
    defanged = defang_url("https://phish.example.com/login")
    assert "hxxps://" in defanged
    assert "[.]" in defanged
    assert "https://" not in defanged


def test_scheme_defaulting():
    """Bare hostnames or schemeless targets must default to https."""
    norm = normalize_url("example.com/test")
    assert norm.scheme == "https"
    assert norm.normalized_url == "https://example.com/test"


def test_hostname_lowercasing_and_trailing_dots():
    """Hostnames must be lowercased and trailing FQDN dots removed."""
    norm = normalize_url("HTTPS://SUB.EXAMPLE.COM./PATH")
    assert norm.hostname == "sub.example.com"
    assert norm.normalized_url == "https://sub.example.com/PATH"


def test_default_port_stripping():
    """Default ports 80 for HTTP and 443 for HTTPS must be stripped; custom ports kept."""
    norm_http = normalize_url("http://example.com:80/path")
    assert norm_http.port is None
    assert norm_http.normalized_url == "http://example.com/path"

    norm_https = normalize_url("https://example.com:443/path")
    assert norm_https.port is None
    assert norm_https.normalized_url == "https://example.com/path"

    norm_custom = normalize_url("https://example.com:8443/api")
    assert norm_custom.port == 8443
    assert norm_custom.normalized_url == "https://example.com:8443/api"


def test_embedded_credential_stripping():
    """Embedded credentials must be stripped from the normalized URL and preserved in fields."""
    norm = normalize_url("https://admin:secret123@portal.company.com/dashboard")
    assert norm.username == "admin"
    assert norm.password == "secret123"
    assert "admin" not in norm.normalized_url
    assert "secret123" not in norm.normalized_url
    assert norm.normalized_url == "https://portal.company.com/dashboard"


def test_query_parameter_sorting():
    """Query parameters must be sorted canonically."""
    norm = normalize_url("https://example.com/search?z=9&a=1&m=5")
    assert norm.normalized_url == "https://example.com/search?a=1&m=5&z=9"


def test_sha256_canonical_hashing():
    """Identical logical URLs must produce identical SHA-256 hashes."""
    norm1 = normalize_url("hxxps://EXAMPLE.com:443/login?b=2&a=1")
    norm2 = normalize_url("https://example.com/login?a=1&b=2")
    assert norm1.url_hash == norm2.url_hash
    assert len(norm1.url_hash) == 64


def test_idn_punycode_handling():
    """Internationalized domain names must be converted to Punycode."""
    norm = normalize_url("https://münchen.de")
    assert "xn--" in norm.ascii_host
    assert norm.host.endswith(".de") or norm.ascii_host.endswith(".de")
