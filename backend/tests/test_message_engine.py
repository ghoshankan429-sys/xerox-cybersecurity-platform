import pytest
from app.analyzers.message.normalizer import normalize_message
from app.analyzers.message.extractor import extract_iocs
from app.analyzers.message.engine import analyze_message_heuristics
from app.schemas.threat import EvidenceSeverity


def test_urgency_and_suspension_coercion():
    """Detects urgent psychological manipulation and account termination threats."""
    raw = "CRITICAL ALERT: Your Microsoft 365 account will be suspended within 24 hours due to an unauthorized login."
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)
    res = analyze_message_heuristics(norm, iocs)

    titles = [f.title for f in res.findings]
    assert any("Artificial Time Constraint" in t for t in titles)
    assert any("Account Suspension" in t for t in titles)
    assert "microsoft" in res.detected_brands


def test_credential_harvesting_demands():
    """Detects explicit requests for passwords and OTP/2FA codes."""
    raw = "Security Verification: Please provide your one-time code and enter your password to confirm identity."
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)
    res = analyze_message_heuristics(norm, iocs)

    titles = [f.title for f in res.findings]
    assert any("Password" in t for t in titles)
    assert any("One-Time" in t or "OTP" in t for t in titles)


def test_financial_and_gift_card_fraud():
    """Detects gift card payment demands and crypto wallet transfer lures."""
    raw = "URGENT: Outstanding penalty must be settled immediately via $500 Steam gift cards or to our bitcoin wallet."
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)
    res = analyze_message_heuristics(norm, iocs)

    titles = [f.title for f in res.findings]
    assert any("Gift Card" in t for t in titles)
    assert any("Cryptocurrency" in t for t in titles)


def test_brand_impersonation_with_unrelated_domain():
    """Flags messages claiming to be an institution while linking to an unrelated domain."""
    raw = "USPS Notification: Package delivery on hold due to unpaid customs fee: https://usps-redelivery-support.xyz/auth"
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)
    res = analyze_message_heuristics(norm, iocs)

    titles = [f.title for f in res.findings]
    assert any("Brand Impersonation" in t for t in titles)
    assert any(f.severity == EvidenceSeverity.CRITICAL for f in res.findings if "Brand Impersonation" in f.title)


def test_sender_display_name_spoofing():
    """Detects display name spoofing where sender header claims an official brand but envelope is third-party."""
    raw = "Your monthly invoice is attached."
    sender_header = "PayPal Billing Support <attacker789@free-mail.com>"
    norm = normalize_message(raw, sender=sender_header)
    iocs = extract_iocs(norm)
    res = analyze_message_heuristics(norm, iocs)

    titles = [f.title for f in res.findings]
    assert any("Display Name Deception" in t for t in titles)


def test_benign_message_no_high_severity():
    """Routine corporate or personal messages produce zero high/critical severity findings."""
    raw = (
        "Hi team, let's reschedule our Thursday architecture sync to 3 PM. "
        "The project roadmap has been uploaded to the team drive."
    )
    norm = normalize_message(raw)
    iocs = extract_iocs(norm)
    res = analyze_message_heuristics(norm, iocs)

    assert not any(f.severity in (EvidenceSeverity.HIGH, EvidenceSeverity.CRITICAL) for f in res.findings)
    assert len(res.detected_brands) == 0
