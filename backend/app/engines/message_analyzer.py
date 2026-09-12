import re
from typing import List, Tuple
from app.schemas.threat import (
    TechnicalMetadata,
    EvidenceItem,
    EvidenceCategory,
    EvidenceSeverity,
)
from app.engines.url_analyzer import analyze_url_target

URGENCY_PATTERNS = [
    (r"\b(within\s+\d+\s+(hours?|minutes?|days?))\b", "Explicit Time Constraint Pressure"),
    (r"\b(immediate(ly)?|urgent(ly)?|final notice|critical alert|action required)\b", "Artificial Urgency & Panic Induction"),
    (r"\b(account.*(suspended|terminated|locked|restricted|deactivated))\b", "Account Suspension / Coercion Threat"),
    (r"\b(unauthorized.*(transaction|login|charge|transfer|access))\b", "Fake Security Incident Alarm"),
    (r"\b(verify.*(identity|account|credentials|passcode|ssn|pin))\b", "Direct Identity / Credential Demand"),
    (r"\b(package.*(pending|delivery fee|undelivered|customs hold))\b", "Postal / Logistics Delivery Bait"),
    (r"\b(tax.*(refund|penalty|audit|arrears|irs))\b", "Government Authority / Tax Coercion"),
    (r"\b(winner|lottery|prize|gift card|selected for|reward)\b", "Lottery / Advance Fee Baiting"),
]

URL_REGEX = re.compile(
    r"(?:(?:https?|hxxps?)://|www\.)[^\s/$.?#].[^\s]*|(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|xyz|top|live|info|me|app|dev|co|io|cc|vip|biz|online)[^\s]*",
    re.IGNORECASE,
)

async def analyze_message_content(content: str, sender_metadata: str | None = None) -> tuple[TechnicalMetadata, list[EvidenceItem], list[str]]:
    evidence_items: list[EvidenceItem] = []
    social_flags: list[str] = []
    extracted_urls: list[str] = []

    # 1. Extract URLs
    raw_matches = URL_REGEX.findall(content)
    for m in raw_matches:
        url_cand = m.strip(".,;:()[]'\"")
        if url_cand and url_cand not in extracted_urls:
            extracted_urls.append(url_cand)

    # 2. Check Urgency and Social Engineering Patterns
    content_lower = content.lower()
    for pattern, rule_title in URGENCY_PATTERNS:
        match = re.search(pattern, content_lower)
        if match:
            matched_phrase = match.group(0)
            social_flags.append(rule_title)
            evidence_items.append(
                EvidenceItem(
                    category=EvidenceCategory.CONTENT,
                    severity=EvidenceSeverity.HIGH,
                    title=rule_title,
                    description=f"Message employs psychological manipulation language: '{matched_phrase}'.",
                    technical_proof=f"Matched NLP trigger: '{matched_phrase}'",
                    why_this_matters="Adversaries employ artificial panic and time-urgency heuristics to bypass rational scrutiny and induce impulsive clicks."
                )
            )

    # 3. Sender Metadata Anomalies (if provided)
    if sender_metadata:
        sm_lower = sender_metadata.lower()
        if re.search(r"(\+?[0-9]{10,15})", sender_metadata) and ("bank" in content_lower or "apple" in content_lower or "paypal" in content_lower):
            evidence_items.append(
                EvidenceItem(
                    category=EvidenceCategory.IDENTITY,
                    severity=EvidenceSeverity.HIGH,
                    title="Unofficial Mobile Sender for Institutional Alert",
                    description=f"Message claims to be an official institutional security notice but originated from an unverified mobile/long-code sender: '{sender_metadata}'.",
                    technical_proof=f"Sender: {sender_metadata}",
                    why_this_matters="Legitimate financial and tech corporations utilize verified registered short-codes (5-6 digits) or branded alpha-sender tags, never random peer-to-peer mobile numbers."
                )
            )

    # 4. Synthesize with URL analysis if embedded links are present
    combined_metadata = TechnicalMetadata(
        extracted_urls=extracted_urls,
        social_engineering_flags=social_flags,
    )

    if extracted_urls:
        first_url = extracted_urls[0]
        url_meta, url_evidence, detected_brands = await analyze_url_target(first_url)
        # Merge metadata
        combined_metadata.domain = url_meta.domain
        combined_metadata.subdomain = url_meta.subdomain
        combined_metadata.registered_domain = url_meta.registered_domain
        combined_metadata.tld = url_meta.tld
        combined_metadata.ip_addresses = url_meta.ip_addresses
        combined_metadata.dns = url_meta.dns
        combined_metadata.ssl = url_meta.ssl
        combined_metadata.redirect_hops = url_meta.redirect_hops
        combined_metadata.entropy = url_meta.entropy
        combined_metadata.detected_brands = detected_brands
        # Append URL evidence
        evidence_items.extend(url_evidence)
    else:
        # Message has no links
        if not social_flags:
            evidence_items.append(
                EvidenceItem(
                    category=EvidenceCategory.CONTENT,
                    severity=EvidenceSeverity.INFO,
                    title="No Obvious Coercion Patterns Detected",
                    description="The text payload did not trigger standard algorithmic phishing keywords or urgency heuristics.",
                    technical_proof="Heuristic keyword scan: 0 critical triggers matched",
                    why_this_matters="Clean messages without coercive language or links present minimal immediate security risk."
                )
            )

    return combined_metadata, evidence_items, extracted_urls
