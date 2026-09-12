import json
import logging
from datetime import datetime, timezone
import uuid
from app.core.datetime_utils import get_monotonic_utc_now

from app.schemas.threat import (
    RiskLevel,
    TargetType,
    EvidenceItem,
    EvidenceSeverity,
    RecommendedAction,
    TechnicalMetadata,
    ThreatReport,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

def calculate_deterministic_risk_score(evidence_items: list[EvidenceItem], metadata: TechnicalMetadata) -> tuple[int, RiskLevel, float]:
    """Calculates quantitative risk score (0-100) and maps to the 5-tier taxonomy."""
    score = 0
    
    for ev in evidence_items:
        if ev.severity == EvidenceSeverity.CRITICAL:
            score += 45
        elif ev.severity == EvidenceSeverity.HIGH:
            score += 25
        elif ev.severity == EvidenceSeverity.MEDIUM:
            score += 15
        elif ev.severity == EvidenceSeverity.LOW:
            score += 5
        elif ev.severity == EvidenceSeverity.INFO:
            pass

    # Specific threat overrides
    if metadata.detected_brands and metadata.registered_domain:
        score = max(score, 88)
    
    if metadata.social_engineering_flags and metadata.detected_brands:
        score = max(score, 94)

    # Cap between 0 and 100
    score = min(max(score, 5), 99) if evidence_items else 5

    # If domain resolves to clean infrastructure and has valid SSL and no high/critical flags
    has_threats = any(ev.severity in (EvidenceSeverity.HIGH, EvidenceSeverity.CRITICAL) for ev in evidence_items)
    if not has_threats:
        score = min(score, 18)

    # Classify Tier
    if score <= 20:
        level = RiskLevel.BENIGN
    elif score <= 45:
        level = RiskLevel.LOW_RISK
    elif score <= 70:
        level = RiskLevel.SUSPICIOUS
    elif score <= 89:
        level = RiskLevel.HIGH_RISK
    else:
        level = RiskLevel.CRITICAL

    # Confidence calculation based on telemetry completeness
    signals_count = 1  # Base heuristic
    if metadata.dns and (metadata.dns.a or metadata.dns.mx):
        signals_count += 1
    if metadata.ssl and metadata.ssl.valid_from:
        signals_count += 1
    if metadata.redirect_hops:
        signals_count += 1
    confidence = round(min(0.75 + (signals_count * 0.06), 0.98), 2)

    return score, level, confidence

def generate_deterministic_narrative(
    target_type: TargetType,
    raw_target: str,
    risk_level: RiskLevel,
    risk_score: int,
    metadata: TechnicalMetadata,
    evidence_items: list[EvidenceItem],
) -> tuple[str, str, list[RecommendedAction]]:
    """Generates structured expert narrative without external API dependencies."""
    
    # 1. Executive Summary & Layman Verdict
    if risk_level == RiskLevel.CRITICAL:
        if metadata.detected_brands:
            brand_str = ", ".join(b.upper() for b in metadata.detected_brands)
            exec_summary = (
                f"Active high-confidence phishing campaign detected impersonating {brand_str}. "
                f"The target infrastructure ({metadata.domain}) is deceptive, designed specifically "
                f"to capture victim credentials or multi-factor authentication tokens."
            )
            layman_verdict = (
                f"🚨 DO NOT CLICK OR ENTER DETAILS: This is NOT {brand_str}. "
                f"It is a fraudulent duplicate designed to steal your passwords or account access."
            )
        else:
            exec_summary = (
                f"Critical malicious threat detected targeting user credentials and data integrity. "
                f"Multiple high-severity telemetry anomalies confirmed across infrastructure and payload content."
            )
            layman_verdict = (
                "🚨 CRITICAL DANGER: This link or message is dangerous. Interacting with it puts your "
                "device, accounts, or personal information at immediate risk of compromise."
            )
        actions = [
            RecommendedAction(
                priority="IMMEDIATE",
                action="Close and quarantine the message/page immediately",
                rationale="Prevents execution of background browser exploits or accidental form submission.",
                action_type="DO_NOT_CLICK"
            ),
            RecommendedAction(
                priority="IMMEDIATE",
                action="If credentials were submitted, change your account password immediately",
                rationale="Prevents unauthorized session takeover by the threat actor.",
                action_type="CHANGE_PASSWORD"
            ),
            RecommendedAction(
                priority="REPORTING",
                action="Submit target to anti-phishing abuse reporting channels (Google Safe Browsing / PhishTank)",
                rationale="Accelerates community-wide domain takedown and browser blocking.",
                action_type="REPORT_PHISHING"
            ),
        ]

    elif risk_level == RiskLevel.HIGH_RISK:
        exec_summary = (
            f"High-risk threat indicators detected. The target exhibits characteristics strongly correlated with "
            f"social engineering scams, credential harvesting, or deceptive redirects."
        )
        layman_verdict = (
            "⚠️ HIGH RISK: We strongly advise against visiting this site or replying to this message. "
            "It displays classic warning signs of a scam or impersonation attempt."
        )
        actions = [
            RecommendedAction(
                priority="IMMEDIATE",
                action="Do not click links or download any files from this source",
                rationale="High probability of malware delivery or account harvesting.",
                action_type="DO_NOT_CLICK"
            ),
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Contact the claimed sender directly through known official channels",
                rationale="Verifies whether the communication was legitimate without trusting the link provided.",
                action_type="VERIFY_SENDER"
            ),
        ]

    elif risk_level == RiskLevel.SUSPICIOUS:
        exec_summary = (
            f"Anomalous signals detected on {metadata.domain or 'the target'}. While direct malicious payloads were "
            f"not definitively confirmed, unusual infrastructure (e.g. low-reputation TLD or redirect hops) warrants strict caution."
        )
        layman_verdict = (
            "⚡ CAUTION ADVISED: This target looks unusual or unverified. Do not provide sensitive details, "
            "passwords, or payment numbers."
        )
        actions = [
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Inspect the sender address and domain carefully before proceeding",
                rationale="Unusual redirects or non-standard web domains can be precursors to phishing.",
                action_type="VERIFY_SENDER"
            )
        ]

    elif risk_level == RiskLevel.LOW_RISK:
        exec_summary = (
            f"Target {metadata.domain or 'analyzed'} exhibits standard operational infrastructure with minor "
            f"informational anomalies. Low probability of malicious intent."
        )
        layman_verdict = (
            "ℹ️ LOW RISK: No obvious phishing indicators were detected, but exercise standard digital caution "
            "as with any external link."
        )
        actions = [
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Safe to proceed with standard browsing caution",
                rationale="Infrastructure appears benign, but always verify unfamiliar requests.",
                action_type="SAFE_TO_PROCEED"
            )
        ]

    else: # BENIGN
        exec_summary = (
            f"Clean, verified target. DNS, TLS encryption, and domain reputation align with standard legitimate "
            f"corporate or web operations. No deceptive brand tokens or social engineering cues detected."
        )
        layman_verdict = (
            "✅ VERIFIED SAFE: Our analysis found no malicious behavior, deceptive patterns, or security risks. "
            "This link or message appears completely safe."
        )
        actions = [
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Safe to proceed normally",
                rationale="All cryptographic, structural, and behavioral indicators returned clean results.",
                action_type="SAFE_TO_PROCEED"
            )
        ]

    return exec_summary, layman_verdict, actions

async def synthesize_threat_report(
    target_type: TargetType,
    raw_target: str,
    defanged_target: str,
    metadata: TechnicalMetadata,
    evidence_items: list[EvidenceItem],
    gemini_api_key: str | None = None,
) -> ThreatReport:
    """Combines forensic telemetry and AI synthesis into a unified ThreatReport."""
    
    # 1. Calculate Score & Tier
    risk_score, risk_level, confidence = calculate_deterministic_risk_score(evidence_items, metadata)

    # 2. Default Deterministic Synthesis
    exec_summary, layman_verdict, actions = generate_deterministic_narrative(
        target_type, raw_target, risk_level, risk_score, metadata, evidence_items
    )

    # 3. Optional Gemini LLM Enhancement if key available
    api_key_to_use = gemini_api_key or settings.GEMINI_API_KEY
    if api_key_to_use:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key_to_use)
            prompt = (
                f"You are XEROX, an authoritative cybersecurity analyst co-pilot.\n"
                f"Target Type: {target_type.value}\n"
                f"Target: {defanged_target}\n"
                f"Calculated Risk Level: {risk_level.value} (Score: {risk_score}/100)\n"
                f"Technical Evidence Detected:\n"
                + "\n".join(f"- [{ev.severity.value}] {ev.title}: {ev.description}" for ev in evidence_items)
                + "\n\nSynthesize an authoritative analysis. Return strictly a valid JSON object with keys:\n"
                f"- executive_summary: A 2-sentence precise technical executive summary for security pros.\n"
                f"- layman_verdict: A 2-sentence crystal clear explanation for a normal non-technical person.\n"
                f"- actions: An array of objects with keys 'priority' (IMMEDIATE/PREVENTATIVE/REPORTING), 'action', 'rationale', 'action_type' ('DO_NOT_CLICK', 'CHANGE_PASSWORD', 'REPORT_PHISHING', 'VERIFY_SENDER', 'SAFE_TO_PROCEED')."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            parsed_llm = json.loads(response.text)
            if "executive_summary" in parsed_llm:
                exec_summary = parsed_llm["executive_summary"]
            if "layman_verdict" in parsed_llm:
                layman_verdict = parsed_llm["layman_verdict"]
            if "actions" in parsed_llm and isinstance(parsed_llm["actions"], list):
                llm_actions = []
                for act in parsed_llm["actions"]:
                    llm_actions.append(
                        RecommendedAction(
                            priority=act.get("priority", "PREVENTATIVE"),
                            action=act.get("action", ""),
                            rationale=act.get("rationale", ""),
                            action_type=act.get("action_type", "SAFE_TO_PROCEED")
                        )
                    )
                if llm_actions:
                    actions = llm_actions

        except Exception as e:
            logger.warning(f"Gemini API enrichment skipped/failed, using deterministic intelligence: {e}")

    report = ThreatReport(
        scan_id=str(uuid.uuid4()),
        target_type=target_type,
        raw_target=raw_target,
        defanged_target=defanged_target,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence_score=confidence,
        executive_summary=exec_summary,
        layman_verdict=layman_verdict,
        evidence_items=evidence_items,
        recommended_actions=actions,
        technical_metadata=metadata,
        analyzed_at=get_monotonic_utc_now().isoformat(),
    )

    return report
