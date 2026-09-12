import pytest
from app.analyzers.screenshot.normalizer import normalize_ocr_text
from app.analyzers.screenshot.vision.base import VisionExtractionResult
from app.analyzers.screenshot.engine import analyze_screenshot_heuristics
from app.schemas.threat import EvidenceSeverity


def test_suspicious_login_form_detection():
    ocr = normalize_ocr_text("Sign in to your account. Enter your email and password.")
    vision = VisionExtractionResult(
        raw_text=ocr.raw_text,
        visual_elements=["login_form", "password_field"],
        is_available=True,
    )
    result = analyze_screenshot_heuristics(ocr, vision, extracted_urls=[], extracted_domains=[])

    assert result.has_login_form is True
    assert any(f.title == "Suspicious Visual Authentication / Login Interface" for f in result.findings)


def test_credential_harvesting_secret_phrases():
    ocr = normalize_ocr_text("Confirm your 12-word secret recovery phrase or private key to restore wallet access.")
    vision = VisionExtractionResult(raw_text=ocr.raw_text, is_available=True)
    result = analyze_screenshot_heuristics(ocr, vision, extracted_urls=[], extracted_domains=[])

    assert result.has_credential_harvesting is True
    assert any(f.severity == EvidenceSeverity.CRITICAL for f in result.findings)


def test_counterfeit_antivirus_tech_support_alert():
    ocr = normalize_ocr_text("Windows Defender Alert: Critical threat detected (Trojan spyware). Call Microsoft support at 1-800-555-0199 immediately.")
    vision = VisionExtractionResult(raw_text=ocr.raw_text, visual_elements=["security_alert_banner"], is_available=True)
    result = analyze_screenshot_heuristics(ocr, vision, extracted_urls=[], extracted_domains=[])

    assert result.has_counterfeit_alert is True
    assert any(f.title == "Deceptive Security Warning / Tech Support Lure" for f in result.findings)


def test_qr_code_and_crypto_payment_demands():
    ocr = normalize_ocr_text("Scan the QR code below to transfer 0.05 BTC to release package delivery.")
    vision = VisionExtractionResult(raw_text=ocr.raw_text, visual_elements=["qr_code"], is_available=True)
    result = analyze_screenshot_heuristics(ocr, vision, extracted_urls=[], extracted_domains=[])

    assert result.has_payment_or_qr is True
    assert any(f.title == "Unsolicited QR Code / Crypto / Gift Card Demands" for f in result.findings)


def test_brand_logo_mismatch_with_unrelated_domain():
    ocr = normalize_ocr_text("Welcome to Microsoft 365 Portal. Continue to mailbox.")
    vision = VisionExtractionResult(
        raw_text=ocr.raw_text,
        detected_brands=["Microsoft"],
        visible_domains=["ms-portal-auth.xyz"],
        is_available=True,
    )
    result = analyze_screenshot_heuristics(
        ocr,
        vision,
        extracted_urls=["https://ms-portal-auth.xyz/login"],
        extracted_domains=["ms-portal-auth.xyz"],
    )

    assert result.has_brand_spoofing is True
    assert any("Visual Brand Mismatch: Microsoft" in f.title for f in result.findings)


def test_fake_robot_verification_captcha_lure():
    ocr = normalize_ocr_text("Cloudflare Verification: Click allow to verify you are not a robot.")
    vision = VisionExtractionResult(raw_text=ocr.raw_text, visual_elements=["captcha_verification"], is_available=True)
    result = analyze_screenshot_heuristics(ocr, vision, extracted_urls=[], extracted_domains=[])

    assert any(f.title == "Fake Robot Verification / Browser Notification Lure" for f in result.findings)


def test_benign_screenshot_no_high_severity():
    ocr = normalize_ocr_text("Weekly Team Sync: Q3 Engineering Goals and Architecture Review. Agenda: 1. Deployments 2. Documentation.")
    vision = VisionExtractionResult(
        raw_text=ocr.raw_text,
        visual_elements=["presentation_slide"],
        is_available=True,
    )
    result = analyze_screenshot_heuristics(ocr, vision, extracted_urls=[], extracted_domains=[])

    assert result.has_login_form is False
    assert result.has_credential_harvesting is False
    assert result.has_counterfeit_alert is False
    assert result.has_brand_spoofing is False
    assert len([f for f in result.findings if f.severity in (EvidenceSeverity.HIGH, EvidenceSeverity.CRITICAL)]) == 0
