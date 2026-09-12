import pytest
from app.analyzers.url.normalizer import normalize_url
from app.analyzers.url.engine import analyze_url_heuristics
from app.schemas.threat import EvidenceSeverity


def test_brand_impersonation_detection():
    """Detects brand names in untrusted domains/subdomains."""
    norm = normalize_url("https://paypal-security-verification.serveo.net/login")
    result = analyze_url_heuristics(norm)
    titles = [f.title for f in result.findings]
    assert any("Brand Impersonation" in t for t in titles)
    assert "paypal" in result.metadata.detected_brands


def test_high_risk_tld_detection():
    """Flags domains using known abuse-heavy top-level domains."""
    norm = normalize_url("https://secure-portal.top/auth")
    result = analyze_url_heuristics(norm)
    severities = [f.severity for f in result.findings if "Top-Level Domain" in f.title]
    assert len(severities) > 0
    assert severities[0] in (EvidenceSeverity.MEDIUM, EvidenceSeverity.HIGH)


def test_ephemeral_hosting_detection():
    """Flags abuse-prone free tunnel or cloud hosting endpoints."""
    norm = normalize_url("https://corporate-login.ngrok-free.app/oauth")
    result = analyze_url_heuristics(norm)
    titles = [f.title for f in result.findings]
    assert any("Tunnel" in t or "Ephemeral" in t or "Hosting Abuse" in t for t in titles)


def test_excessive_subdomain_depth():
    """Flags subdomains with 4 or more label tiers."""
    norm = normalize_url("https://a.b.c.d.evil-domain.com/landing")
    result = analyze_url_heuristics(norm)
    titles = [f.title for f in result.findings]
    assert any("Subdomain Depth" in t for t in titles)


def test_raw_ip_hostname():
    """Flags raw IP addresses used as target hostnames."""
    norm = normalize_url("http://93.184.216.34/login.php")
    result = analyze_url_heuristics(norm)
    titles = [f.title for f in result.findings]
    assert any("Direct Public IP" in t for t in titles)


def test_private_network_loopback_flag():
    """Flags loopback or internal IPs as critical SSRF risk."""
    norm = normalize_url("http://127.0.0.1/admin")
    result = analyze_url_heuristics(norm)
    assert result.is_private_network is True
    assert any(f.severity == EvidenceSeverity.CRITICAL for f in result.findings)


def test_embedded_credentials_finding():
    """Flags URLs with embedded user credentials."""
    norm = normalize_url("https://root:password123@target-domain.com/")
    result = analyze_url_heuristics(norm)
    titles = [f.title for f in result.findings]
    assert any("Credentials" in t for t in titles)


def test_dangerous_file_extensions():
    """Flags URLs directly ending in dangerous executable or script extensions."""
    norm = normalize_url("https://sharepoint-docs.online/invoice.scr")
    result = analyze_url_heuristics(norm)
    titles = [f.title for f in result.findings]
    assert any("Direct Executable" in t or "Download Target" in t for t in titles)


def test_open_redirect_parameters():
    """Flags suspicious unvalidated redirect query parameters."""
    norm = normalize_url("https://legit-service.com/login?redirect=https://attacker.com")
    result = analyze_url_heuristics(norm)
    titles = [f.title for f in result.findings]
    assert any("Open Redirect" in t for t in titles)


def test_benign_url_minimal_findings():
    """Legitimate enterprise domains have zero high/critical severity findings."""
    norm = normalize_url("https://www.google.com/search?q=cybersecurity")
    result = analyze_url_heuristics(norm)
    assert not any(f.severity in (EvidenceSeverity.HIGH, EvidenceSeverity.CRITICAL) for f in result.findings)
    assert result.is_private_network is False
