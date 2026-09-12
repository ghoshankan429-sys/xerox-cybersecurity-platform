import re
from dataclasses import dataclass, field
from typing import List, Optional

from app.analyzers.message.normalizer import NormalizedMessage
from app.analyzers.message.extractor import ExtractedIOCs
from app.schemas.threat import (
    EvidenceItem,
    EvidenceCategory,
    EvidenceSeverity,
)

# 1. Targeted Institutional Brands & Legitimate Root Domains
KNOWN_INSTITUTIONAL_BRANDS = {
    "usps": {
        "name": "United States Postal Service (USPS)",
        "domains": ["usps.com", "uspspostalp.com"],
        "keywords": ["usps", "postal service", "post office", "priority mail"],
    },
    "fedex": {
        "name": "FedEx",
        "domains": ["fedex.com"],
        "keywords": ["fedex", "federal express"],
    },
    "dhl": {
        "name": "DHL Express",
        "domains": ["dhl.com", "dhl.de"],
        "keywords": ["dhl", "dhl express"],
    },
    "ups": {
        "name": "United Parcel Service (UPS)",
        "domains": ["ups.com"],
        "keywords": ["ups", "united parcel service"],
    },
    "chase": {
        "name": "JPMorgan Chase Bank",
        "domains": ["chase.com", "jpmorgan.com"],
        "keywords": ["chase bank", "chase", "jpmorgan"],
    },
    "bankofamerica": {
        "name": "Bank of America",
        "domains": ["bankofamerica.com", "bofa.com"],
        "keywords": ["bank of america", "bofa"],
    },
    "wellsfargo": {
        "name": "Wells Fargo",
        "domains": ["wellsfargo.com"],
        "keywords": ["wells fargo"],
    },
    "paypal": {
        "name": "PayPal",
        "domains": ["paypal.com"],
        "keywords": ["paypal"],
    },
    "apple": {
        "name": "Apple Inc.",
        "domains": ["apple.com", "icloud.com"],
        "keywords": ["apple id", "icloud", "apple support", "itunes"],
    },
    "microsoft": {
        "name": "Microsoft 365",
        "domains": ["microsoft.com", "office.com", "live.com", "outlook.com", "office365.com"],
        "keywords": ["microsoft", "office 365", "m365", "outlook", "onedrive"],
    },
    "google": {
        "name": "Google / Workspace",
        "domains": ["google.com", "gmail.com"],
        "keywords": ["google account", "google workspace", "gmail verification"],
    },
    "netflix": {
        "name": "Netflix",
        "domains": ["netflix.com"],
        "keywords": ["netflix"],
    },
    "irs": {
        "name": "Internal Revenue Service (IRS)",
        "domains": ["irs.gov"],
        "keywords": ["irs", "internal revenue service", "tax refund", "form 1099"],
    },
}

# 2. Urgency & Coercion Rules
URGENCY_PATTERNS = [
    (
        r"\b(?:within\s+(?:24|12|48|1|2|6)\s*(?:hours?|hrs?|mins?|minutes?)|immediate(?:ly)?|act\s+now|urgent(?:ly)?|time-sensitive)\b",
        "Artificial Time Constraint Pressure",
        EvidenceSeverity.MEDIUM,
        "Message manufactures a strict artificial deadline to induce impulsive victim action before verification.",
    ),
    (
        r"\b(?:account.*(?:suspended|terminated|locked|disabled|restricted|deactivated|closed|frozen)|service.*interruption|access.*revoked)\b",
        "Account Suspension / Coercion Threat",
        EvidenceSeverity.HIGH,
        "Message threatens immediate account termination or suspension to provoke panic.",
    ),
    (
        r"\b(?:unauthorized.*(?:transaction|login|device|charge|activity|access)|fraudulent.*activity|security.*breach|unrecognized.*sign-in)\b",
        "Fake Security Incident Alarm",
        EvidenceSeverity.MEDIUM,
        "Adversary fabricates a non-existent security breach or unauthorized charge to cause panic.",
    ),
    (
        r"\b(?:final\s+notice|last\s+warning|immediate\s+legal\s+action|lawsuit|warrant|arrest|subpoena)\b",
        "Legal & Regulatory Coercion Pressure",
        EvidenceSeverity.HIGH,
        "Threatens severe legal repercussions, lawsuits, or law enforcement action.",
    ),
]

# 3. Credential Harvesting & Secret Demands
CREDENTIAL_PATTERNS = [
    (
        r"\b(?:enter|provide|verify|confirm|update|reset)\s+(?:your\s+)?(?:password|passcode|pin|credentials?|secret)\b",
        "Direct Password / PIN Harvesting Request",
        EvidenceSeverity.HIGH,
        "Direct request for sensitive account passwords or PINs over message channels.",
    ),
    (
        r"\b(?:one-time\s+code|verification\s+code|otp|2fa\s+code|security\s+code|sms\s+code)\b",
        "Multi-Factor Authentication (OTP / 2FA) Interception",
        EvidenceSeverity.HIGH,
        "Attempts to harvest one-time passcodes to bypass multi-factor authentication defenses.",
    ),
    (
        r"\b(?:verify.*(?:identity|ssn|social\s+security|passport|date\s+of\s+birth|mother's\s+maiden))\b",
        "Identity Theft / PII Exfiltration Demand",
        EvidenceSeverity.HIGH,
        "Solicits personal identity attributes (SSN, passport, date of birth) enabling identity theft.",
    ),
]

# 4. Financial & Payment Manipulation Rules
FINANCIAL_PATTERNS = [
    (
        r"\b(?:gift\s+cards?|itunes\s+card|steam\s+card|google\s+play\s+card|apple\s+gift\s+card)\b",
        "Untraceable Gift Card Payment Request",
        EvidenceSeverity.HIGH,
        "Requesting payment via retail gift cards is a definitive indicator of advance-fee fraud.",
    ),
    (
        r"\b(?:bitcoin|btc|cryptocurrency|crypto\s+wallet|usdt|eth|ethereum)\b.*(?:send|deposit|transfer|pay|wallet)",
        "Cryptocurrency Payment / Wallet Transfer Request",
        EvidenceSeverity.HIGH,
        "Demands payment via immutable, irreversible cryptocurrency transactions.",
    ),
    (
        r"\b(?:wire\s+transfer|change.*banking\s+details|update.*direct\s+deposit|new\s+routing\s+number|overdue\s+invoice)\b",
        "Financial Diversion / BEC Wire Fraud Pattern",
        EvidenceSeverity.MEDIUM,
        "Classic Business Email Compromise (BEC) pattern attempting payroll or invoice diversion.",
    ),
    (
        r"\b(?:delivery\s+fee|unpaid\s+shipping|customs\s+duty|redelivery\s+charge|small\s+fee\s+of\s+\$?\d+)\b",
        "Logistics Fee Bait / Credit Card Harvesting",
        EvidenceSeverity.MEDIUM,
        "Tricks victims into entering credit card details for negligible postal or delivery charges.",
    ),
]

# 5. URL Shorteners Often Abused in Smishing
URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "buff.ly", "ow.ly", "cutt.ly", "rb.gy"}


@dataclass
class MessageHeuristicResult:
    """Findings and behavioral metadata produced by deterministic message analysis."""
    findings: List[EvidenceItem] = field(default_factory=list)
    social_engineering_flags: List[str] = field(default_factory=list)
    detected_brands: List[str] = field(default_factory=list)
    extracted_iocs: Optional[ExtractedIOCs] = None


def analyze_message_heuristics(
    message: NormalizedMessage,
    iocs: ExtractedIOCs,
) -> MessageHeuristicResult:
    """Performs deterministic social engineering, deception, and phishing analysis on message content.
    
    CRITICAL SECURITY GUARANTEE:
    This function performs ZERO network requests, socket calls, or external queries.
    """
    findings: List[EvidenceItem] = []
    social_flags: List[str] = []
    detected_brands: List[str] = []

    full_text = f"{message.subject or ''}\n{message.normalized_content}".lower()

    # 1. Evaluate Urgency & Coercion Patterns
    for pattern, title, severity, why_matters in URGENCY_PATTERNS:
        match = re.search(pattern, full_text)
        if match:
            trigger_text = match.group(0)
            social_flags.append(title)
            findings.append(
                EvidenceItem(
                    category=EvidenceCategory.CONTENT,
                    severity=severity,
                    title=title,
                    description=f"Message utilizes psychological pressure: '{trigger_text}'.",
                    technical_proof=f"Matched NLP expression: '{trigger_text}'",
                    why_this_matters=why_matters,
                )
            )

    # 2. Evaluate Credential Demands
    for pattern, title, severity, why_matters in CREDENTIAL_PATTERNS:
        match = re.search(pattern, full_text)
        if match:
            trigger_text = match.group(0)
            social_flags.append(title)
            findings.append(
                EvidenceItem(
                    category=EvidenceCategory.IDENTITY,
                    severity=severity,
                    title=title,
                    description=f"Direct solicitation of confidential credentials detected: '{trigger_text}'.",
                    technical_proof=f"Matched credential trigger: '{trigger_text}'",
                    why_this_matters=why_matters,
                )
            )

    # 3. Evaluate Financial & Payment Manipulation
    for pattern, title, severity, why_matters in FINANCIAL_PATTERNS:
        match = re.search(pattern, full_text)
        if match:
            trigger_text = match.group(0)
            social_flags.append(title)
            findings.append(
                EvidenceItem(
                    category=EvidenceCategory.CONTENT,
                    severity=severity,
                    title=title,
                    description=f"Financial manipulation trigger detected: '{trigger_text}'.",
                    technical_proof=f"Matched financial trigger: '{trigger_text}'",
                    why_this_matters=why_matters,
                )
            )

    # 4. Brand Impersonation & Domain Mismatch Detection
    for brand_key, brand_info in KNOWN_INSTITUTIONAL_BRANDS.items():
        # Check if brand is referenced in text or subject
        is_brand_mentioned = any(kw in full_text for kw in brand_info["keywords"])
        if is_brand_mentioned:
            detected_brands.append(brand_key)

            # Check whether extracted URLs or domains match legitimate domains
            if iocs.domains:
                has_legit_domain = False
                unrelated_domains = []

                for domain in iocs.domains:
                    domain_clean = domain.lower().strip()
                    if any(domain_clean == legit or domain_clean.endswith(f".{legit}") for legit in brand_info["domains"]):
                        has_legit_domain = True
                    else:
                        unrelated_domains.append(domain_clean)

                if not has_legit_domain and unrelated_domains:
                    findings.append(
                        EvidenceItem(
                            category=EvidenceCategory.IDENTITY,
                            severity=EvidenceSeverity.CRITICAL,
                            title=f"Brand Impersonation / Domain Mismatch ({brand_info['name']})",
                            description=(
                                f"Message claims to represent {brand_info['name']}, but all extracted web destinations "
                                f"({', '.join(unrelated_domains[:3])}) are unaffiliated with official domains ({', '.join(brand_info['domains'])})."
                            ),
                            technical_proof=(
                                f"Claimed Brand: {brand_info['name']} | Extracted Domains: {', '.join(unrelated_domains[:3])} | "
                                f"Legitimate Domains: {', '.join(brand_info['domains'])}"
                            ),
                            why_this_matters=(
                                "Severe credential phishing indicator. Attackers routinely reference trusted enterprise names "
                                "in lure text while routing clicks to rogue landing pages."
                            ),
                        )
                    )

    # 5. Sender Metadata & Header Anomalies
    sender_info = f"{message.sender or ''} {message.sender_metadata or ''}".strip()
    if sender_info:
        sender_lower = sender_info.lower()

        # Check for peer-to-peer mobile sender on institutional bank/carrier alerts
        is_long_code_mobile = bool(re.search(r"\+?[0-9]{10,15}", sender_info))
        if is_long_code_mobile and detected_brands:
            findings.append(
                EvidenceItem(
                    category=EvidenceCategory.IDENTITY,
                    severity=EvidenceSeverity.HIGH,
                    title="Unofficial Mobile Sender for Institutional Alert",
                    description=(
                        f"Message references official institutions ({', '.join(b.upper() for b in detected_brands)}) "
                        f"but originated from an unverified mobile/long-code address: '{sender_info}'."
                    ),
                    technical_proof=f"Sender: {sender_info} | Brands: {', '.join(detected_brands)}",
                    why_this_matters=(
                        "Legitimate enterprise organizations dispatch automated security notifications from registered "
                        "dedicated short-codes (5-6 digits) or verified sender envelopes, never personal mobile numbers."
                    ),
                )
            )

        # Check for sender display name spoofing (e.g. "PayPal Support <hack789@gmail.com>")
        if "<" in sender_info and "@" in sender_info:
            display_name = sender_info.split("<")[0].lower().strip()
            envelope = sender_info.split("<")[1].split(">")[0].lower().strip()
            for brand_key, brand_info in KNOWN_INSTITUTIONAL_BRANDS.items():
                if any(kw in display_name for kw in brand_info["keywords"]):
                    if not any(envelope.endswith(f"@{d}") or envelope.endswith(f".{d}") for d in brand_info["domains"]):
                        findings.append(
                            EvidenceItem(
                                category=EvidenceCategory.IDENTITY,
                                severity=EvidenceSeverity.CRITICAL,
                                title=f"Sender Display Name Deception ({brand_info['name']})",
                                description=(
                                    f"Sender claims display name '{display_name}' but the actual return address "
                                    f"'{envelope}' belongs to an unaccredited third-party domain."
                                ),
                                technical_proof=f"Display: '{display_name}' | Actual Envelope: '{envelope}'",
                                why_this_matters=(
                                    "Display name spoofing is the predominant mechanism used in executive and banking impersonation."
                                ),
                            )
                        )

    # 6. Suspicious URL Shorteners in High-Urgency Messages
    if iocs.domains:
        shorteners_detected = [d for d in iocs.domains if d in URL_SHORTENERS]
        if shorteners_detected:
            findings.append(
                EvidenceItem(
                    category=EvidenceCategory.INFRASTRUCTURE,
                    severity=EvidenceSeverity.MEDIUM,
                    title="URL Shortener Concealment in Message",
                    description=(
                        f"Message utilizes URL shortener service ({', '.join(shorteners_detected)}) "
                        "to obscure the final web destination."
                    ),
                    technical_proof=f"Shortener domains detected: {', '.join(shorteners_detected)}",
                    why_this_matters=(
                        "URL shorteners hide final landing page hosts, complicating pre-click inspection and evading perimeter scanners."
                    ),
                )
            )

    return MessageHeuristicResult(
        findings=findings,
        social_engineering_flags=social_flags,
        detected_brands=detected_brands,
        extracted_iocs=iocs,
    )
