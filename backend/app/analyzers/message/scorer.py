from dataclasses import dataclass
from typing import List, Optional

from app.schemas.threat import (
    RiskLevel,
    EvidenceItem,
    EvidenceSeverity,
    RecommendedAction,
)


@dataclass(frozen=True)
class MessageRiskAssessment:
    score: int
    level: RiskLevel
    confidence: float
    layman_verdict: str
    executive_summary: str
    recommended_actions: List[RecommendedAction]


# Quantitative scoring weights per finding severity
SEVERITY_WEIGHTS = {
    EvidenceSeverity.CRITICAL: 50,
    EvidenceSeverity.HIGH: 25,
    EvidenceSeverity.MEDIUM: 12,
    EvidenceSeverity.LOW: 5,
    EvidenceSeverity.INFO: 0,
}


def calculate_message_risk_score(
    message_findings: List[EvidenceItem],
    url_findings: List[EvidenceItem],
    url_max_score: int = 0,
    has_correlation: bool = False,
) -> MessageRiskAssessment:
    """Calculates transparent, deterministic risk score (0-100) combining message and URL indicators.
    
    Prevents duplicate penalty while properly boosting composite attack vectors.
    """
    raw_score = 0
    max_severity = EvidenceSeverity.INFO

    # 1. Score message findings
    for finding in message_findings:
        weight = SEVERITY_WEIGHTS.get(finding.severity, 5)
        raw_score += weight
        if finding.severity == EvidenceSeverity.CRITICAL:
            max_severity = EvidenceSeverity.CRITICAL
        elif finding.severity == EvidenceSeverity.HIGH and max_severity != EvidenceSeverity.CRITICAL:
            max_severity = EvidenceSeverity.HIGH
        elif finding.severity == EvidenceSeverity.MEDIUM and max_severity not in (EvidenceSeverity.CRITICAL, EvidenceSeverity.HIGH):
            max_severity = EvidenceSeverity.MEDIUM

    # 2. Factor in URL findings and URL max score without direct duplication
    if url_max_score >= 70:
        # High or Critical URL in message directly elevates overall score
        raw_score = max(raw_score, url_max_score)
        if url_max_score >= 90:
            max_severity = EvidenceSeverity.CRITICAL
        elif max_severity != EvidenceSeverity.CRITICAL:
            max_severity = EvidenceSeverity.HIGH
    elif url_max_score >= 40:
        raw_score += int(url_max_score * 0.4)
    elif url_max_score >= 15:
        raw_score += 10

    # 3. Correlation amplifier: Message social engineering paired with high-risk URL
    if has_correlation:
        raw_score += 25
        if max_severity != EvidenceSeverity.CRITICAL:
            max_severity = EvidenceSeverity.HIGH

    # Enforce minimum risk floor for affirmative critical indicators
    if max_severity == EvidenceSeverity.CRITICAL:
        raw_score = max(raw_score, 75)

    # 4. Enforce bounds
    final_score = min(100, max(0, raw_score))

    # 5. Map score to RiskLevel taxonomy
    if final_score >= 90:
        level = RiskLevel.CRITICAL
    elif final_score >= 70:
        level = RiskLevel.HIGH_RISK
    elif final_score >= 40:
        level = RiskLevel.SUSPICIOUS
    elif final_score >= 16:
        level = RiskLevel.LOW_RISK
    else:
        level = RiskLevel.BENIGN

    # 6. Confidence Score
    total_findings = len(message_findings) + len(url_findings)
    if total_findings >= 3 or final_score >= 70:
        confidence = 95.0
    elif total_findings >= 1:
        confidence = 90.0
    else:
        confidence = 85.0

    # 7. Layman Verdict and Executive Summary
    if level == RiskLevel.CRITICAL:
        layman_verdict = "🚨 FRAUDULENT PHISHING LURE — DO NOT ENGAGE"
        executive_summary = (
            f"High-confidence phishing campaign detected ({total_findings} composite indicators). "
            "Evidence indicates active brand impersonation, urgent coercion, and/or deceptive web infrastructure. "
            "Do not click links, provide passwords, or send funds."
        )
    elif level == RiskLevel.HIGH_RISK:
        layman_verdict = "⚠️ HIGH RISK DECEPTIVE MESSAGE — ACTION NOT RECOMMENDED"
        executive_summary = (
            f"Strong deceptive markers detected ({total_findings} indicators). Message incorporates artificial urgency, "
            "credential harvesting cues, or suspicious redirect targets."
        )
    elif level == RiskLevel.SUSPICIOUS:
        layman_verdict = "⚡ CAUTION ADVISED — POTENTIAL SOCIAL ENGINEERING"
        executive_summary = (
            "Message contains anomalous pressure triggers or unverified sender indicators. "
            "Verify with the claimed sender through an independent, trusted channel before taking action."
        )
    elif level == RiskLevel.LOW_RISK:
        layman_verdict = "ℹ️ LOW RISK — ROUTINE COMMUNICATION"
        executive_summary = (
            "Standard conversational or informational message with minor anomalies. Low probability of malicious intent."
        )
    else:
        layman_verdict = "✅ VERIFIED BENIGN — NO DECEPTIVE PATTERNS DETECTED"
        executive_summary = (
            "Deterministic heuristic checks detected zero coercive language, credential solicitation, or hostile links. "
            "Message aligns with standard baseline communication."
        )

    # 8. Contextual Recommended Actions
    actions = generate_message_recommended_actions(level)

    return MessageRiskAssessment(
        score=final_score,
        level=level,
        confidence=confidence,
        layman_verdict=layman_verdict,
        executive_summary=executive_summary,
        recommended_actions=actions,
    )


def generate_message_recommended_actions(level: RiskLevel) -> List[RecommendedAction]:
    """Generates prioritized contextual mitigation actions based on assessed risk tier."""
    actions: List[RecommendedAction] = []
    if level in (RiskLevel.CRITICAL, RiskLevel.HIGH_RISK):
        actions.append(
            RecommendedAction(
                priority="IMMEDIATE",
                action="Do not click embedded links or reply with sensitive information",
                rationale="Prevents credential harvesting, device fingerprinting, or malware delivery.",
                action_type="DO_NOT_CLICK",
            )
        )
        actions.append(
            RecommendedAction(
                priority="IMMEDIATE",
                action="If credentials or payment codes were provided, rotate passwords immediately",
                rationale="Neutralizes active session takeover or unauthorized fund diversion.",
                action_type="CHANGE_PASSWORD",
            )
        )
        actions.append(
            RecommendedAction(
                priority="REPORTING",
                action="Report message to corporate IT security or carrier spam gateway (e.g. forward to 7726)",
                rationale="Facilitates perimeter carrier blocking and telemetry blacklisting.",
                action_type="REPORT_PHISHING",
            )
        )
    elif level == RiskLevel.SUSPICIOUS:
        actions.append(
            RecommendedAction(
                priority="IMMEDIATE",
                action="Verify communication through an independent official channel",
                rationale="Never trust contact information, phone numbers, or links provided in the message itself.",
                action_type="VERIFY_SENDER",
            )
        )
    else:
        actions.append(
            RecommendedAction(
                priority="IMMEDIATE",
                action="Safe to proceed with normal digital security awareness",
                rationale="No affirmative threat indicators or deceptive triggers were identified.",
                action_type="SAFE_TO_PROCEED",
            )
        )
    return actions
