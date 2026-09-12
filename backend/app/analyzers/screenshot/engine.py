import re
from dataclasses import dataclass, field
from typing import List, Set
from app.schemas.threat import EvidenceItem, EvidenceCategory, EvidenceSeverity
from app.analyzers.screenshot.normalizer import NormalizedOCR
from app.analyzers.screenshot.vision.base import VisionExtractionResult


# Known high-profile brand domain mappings for visual brand spoofing detection
BRAND_LEGIT_DOMAINS = {
    "apple": ["apple.com", "icloud.com"],
    "microsoft": ["microsoft.com", "live.com", "office.com", "microsoftonline.com", "windows.com", "azure.com"],
    "google": ["google.com", "accounts.google.com", "gmail.com"],
    "paypal": ["paypal.com"],
    "chase": ["chase.com"],
    "wells fargo": ["wellsfargo.com"],
    "bank of america": ["bankofamerica.com"],
    "netflix": ["netflix.com"],
    "amazon": ["amazon.com", "aws.amazon.com"],
    "coinbase": ["coinbase.com"],
    "binance": ["binance.com"],
    "usps": ["usps.com"],
    "dhl": ["dhl.com"],
    "fedex": ["fedex.com"],
    "irs": ["irs.gov"],
    "steam": ["steampowered.com", "steamcommunity.com"],
}


@dataclass(frozen=True)
class ScreenshotHeuristicResult:
    """Findings and visual indicators produced by deterministic screenshot analysis."""
    findings: List[EvidenceItem] = field(default_factory=list)
    has_login_form: bool = False
    has_credential_harvesting: bool = False
    has_counterfeit_alert: bool = False
    has_payment_or_qr: bool = False
    has_brand_spoofing: bool = False
    has_urgency: bool = False
    detected_brands: List[str] = field(default_factory=list)


def analyze_screenshot_heuristics(
    norm_ocr: NormalizedOCR,
    vision: VisionExtractionResult,
    extracted_urls: List[str],
    extracted_domains: List[str],
) -> ScreenshotHeuristicResult:
    """Evaluates screenshot visual cues, OCR text, and extracted network IOCs
    to detect phishing portals, fake alerts, credential traps, and brand spoofing.
    """
    findings: List[EvidenceItem] = []
    text_lower = norm_ocr.normalized_text.lower()
    visual_elements_set: Set[str] = {elem.lower() for elem in vision.visual_elements}

    has_login_form = False
    has_credential_harvesting = False
    has_counterfeit_alert = False
    has_payment_or_qr = False
    has_brand_spoofing = False
    has_urgency = False
    detected_brands: List[str] = list(vision.detected_brands)

    # 1. Suspicious Login Form Detection
    login_form_cues = [
        "sign in", "log in", "enter your password", "username", "password",
        "email or phone", "keep me signed in", "forgot password",
    ]
    matches_form_text = any(cue in text_lower for cue in login_form_cues)
    has_visual_form = "login_form" in visual_elements_set or "password_field" in visual_elements_set

    if has_visual_form or (matches_form_text and ("password" in text_lower or "sign in" in text_lower)):
        has_login_form = True
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.HIGH,
                title="Suspicious Visual Authentication / Login Interface",
                description="The screenshot presents an interactive or visual credential entry portal (login fields / password entry).",
                technical_proof=f"Visual form detected. Text cues: {[c for c in login_form_cues if c in text_lower][:3]}",
                why_this_matters="Phishing kits frequently render authentic-looking login prompts to steal corporate or personal credentials.",
            )
        )

    # 2. Explicit Credential / Secret Harvesting Demands
    secret_harvest_cues = [
        "seed phrase", "secret recovery phrase", "private key", "one-time password",
        "2fa code", "security code", "social security number", "ssn", "mother's maiden",
        "pin number", "atm pin",
    ]
    matched_secrets = [cue for cue in secret_harvest_cues if cue in text_lower]
    if matched_secrets:
        has_credential_harvesting = True
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.IDENTITY,
                severity=EvidenceSeverity.CRITICAL,
                title="High-Value Secret & Credential Solicitation",
                description="The visual frame directly requests ultra-sensitive credentials such as recovery seed phrases, 2FA tokens, or PINs.",
                technical_proof=f"Matched secret keywords: {matched_secrets}",
                why_this_matters="Legitimate institutions never request seed phrases, private keys, or PINs via web prompts or screenshots.",
            )
        )

    # 3. Counterfeit Antivirus / System Alert Lures (Tech Support Scams)
    alert_cues = [
        "windows defender alert", "system infected", "trojan spyware", "critical threat detected",
        "call microsoft support", "call apple support", "call toll-free", "call support at",
        "do not restart your computer", "firewall alert", "error code: 0x", "zeus virus",
    ]
    matched_alerts = [cue for cue in alert_cues if cue in text_lower]
    if matched_alerts or "security_alert_banner" in visual_elements_set:
        has_counterfeit_alert = True
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.HIGH,
                title="Deceptive Security Warning / Tech Support Lure",
                description="The screenshot simulates an operating system alert or antivirus warning prompting the user to call a phone number.",
                technical_proof=f"Alert signals: {matched_alerts or ['visual_security_alert_banner']}",
                why_this_matters="Tech support scams fabricate alarming system errors to coerce victims into calling fraudulent call centers.",
            )
        )

    # 4. QR Code & Fraudulent Payment Demands
    has_qr = "qr_code" in visual_elements_set or "qr code" in text_lower
    payment_cues = [
        "bitcoin", "btc", "ethereum", "usdt", "gift card", "apple gift card",
        "google play card", "western union", "scan to pay", "crypto wallet",
    ]
    matched_payments = [cue for cue in payment_cues if cue in text_lower]
    if has_qr or matched_payments:
        has_payment_or_qr = True
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.HIGH,
                title="Unsolicited QR Code / Crypto / Gift Card Demands",
                description="Visual frame contains a QR code or demands payment via irreversible cryptocurrency or gift card channels.",
                technical_proof=f"QR presence: {has_qr}. Payment indicators: {matched_payments}",
                why_this_matters="Adversaries use QR codes ('quishing') to bypass email gateways and steer mobile users to untrusted payment portals.",
            )
        )

    # 5. Visual Brand Impersonation / Logo Mismatch
    all_domains = [d.lower() for d in (extracted_domains + vision.visible_domains)]
    for brand, legit_domains in BRAND_LEGIT_DOMAINS.items():
        # Check if brand appears in text or detected brands
        brand_detected = (brand in text_lower) or any(brand in b.lower() for b in vision.detected_brands)
        if brand_detected:
            if brand not in detected_brands:
                detected_brands.append(brand.title())
            # Check if any legitimate domain for this brand is present
            has_legit_domain = any(any(dom.endswith(ld) for ld in legit_domains) for dom in all_domains)
            # If URLs or domains were found but none match the brand's legitimate domain
            if all_domains and not has_legit_domain:
                has_brand_spoofing = True
                findings.append(
                    EvidenceItem(
                        category=EvidenceCategory.IDENTITY,
                        severity=EvidenceSeverity.HIGH,
                        title=f"Visual Brand Mismatch: {brand.title()}",
                        description=f"Visual frame displays {brand.title()} branding, but visible web domains ({all_domains[:3]}) do not belong to official {brand.title()} infrastructure.",
                        technical_proof=f"Claimed brand: '{brand.title()}'. Expected domains: {legit_domains}. Extracted: {all_domains[:3]}",
                        why_this_matters="Brand impersonation paired with third-party domain hosting is a primary indicator of phishing portals.",
                    )
                )

    # 6. Urgent Action & Countdown Pressure
    urgency_cues = [
        "expires in", "within 24 hours", "within 12 hours", "immediate action required",
        "account will be deleted", "access terminated", "final notice",
    ]
    matched_urgency = [cue for cue in urgency_cues if cue in text_lower]
    if matched_urgency or "countdown_timer" in visual_elements_set:
        has_urgency = True
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.MEDIUM,
                title="Psychological Urgency & Artificial Deadlines",
                description="Visual frame deploys countdown pressure or immediate threats of account loss to impair user deliberation.",
                technical_proof=f"Urgency cues: {matched_urgency or ['visual_countdown_timer']}",
                why_this_matters="Artificial urgency is a standard social engineering tactic to rush victims into compliance.",
            )
        )

    # 7. Fake Robot Verification / CAPTCHA Bypass Lure
    captcha_cues = [
        "verify you are not a robot", "click allow to continue", "press allow to verify",
        "robot check", "i'm not a robot", "captcha verification",
    ]
    matched_captcha = [cue for cue in captcha_cues if cue in text_lower]
    if matched_captcha or "captcha_verification" in visual_elements_set:
        findings.append(
            EvidenceItem(
                category=EvidenceCategory.CONTENT,
                severity=EvidenceSeverity.HIGH,
                title="Fake Robot Verification / Browser Notification Lure",
                description="The image simulates a CAPTCHA or 'click allow' prompt designed to hijack browser notifications or drop malware.",
                technical_proof=f"Matched lures: {matched_captcha or ['captcha_verification']}",
                why_this_matters="Malicious portals use fake verification prompts to trick users into enabling push notification spam or running scripts.",
            )
        )

    return ScreenshotHeuristicResult(
        findings=findings,
        has_login_form=has_login_form,
        has_credential_harvesting=has_credential_harvesting,
        has_counterfeit_alert=has_counterfeit_alert,
        has_payment_or_qr=has_payment_or_qr,
        has_brand_spoofing=has_brand_spoofing,
        has_urgency=has_urgency,
        detected_brands=detected_brands,
    )
