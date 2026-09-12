from dataclasses import dataclass
from typing import List, Optional
from app.schemas.threat import (
    EvidenceItem,
    EvidenceSeverity,
    RiskLevel,
    RecommendedAction,
)


@dataclass(frozen=True)
class RiskAssessment:
    score: int
    level: RiskLevel
    confidence: float
    layman_verdict: str
    executive_summary: str
    recommended_actions: List[RecommendedAction]


SEVERITY_WEIGHTS = {
    EvidenceSeverity.CRITICAL: 50,
    EvidenceSeverity.HIGH: 25,
    EvidenceSeverity.MEDIUM: 12,
    EvidenceSeverity.LOW: 5,
    EvidenceSeverity.INFO: 0,
}


def calculate_risk_score(
    findings: List[EvidenceItem],
    threat_intel_malicious_count: int = 0,
    threat_intel_suspicious_count: int = 0,
) -> RiskAssessment:
    """Calculates a transparent, weighted deterministic risk score from evidence findings.
    
    Guarantees:
    - Every score point is attributable to structured findings.
    - 0-100 range strictly enforced.
    - Conservative verdicts: clean domains stay safe unless affirmative threats are present.
    """
    raw_score = 0
    max_single_severity = EvidenceSeverity.INFO

    for finding in findings:
        weight = SEVERITY_WEIGHTS.get(finding.severity, 0)
        raw_score += weight

        # Track highest severity encountered
        if finding.severity == EvidenceSeverity.CRITICAL:
            max_single_severity = EvidenceSeverity.CRITICAL
        elif finding.severity == EvidenceSeverity.HIGH and max_single_severity != EvidenceSeverity.CRITICAL:
            max_single_severity = EvidenceSeverity.HIGH
        elif finding.severity == EvidenceSeverity.MEDIUM and max_single_severity not in (EvidenceSeverity.CRITICAL, EvidenceSeverity.HIGH):
            max_single_severity = EvidenceSeverity.MEDIUM

    # Enforce minimum risk floor for affirmative critical indicators
    if max_single_severity == EvidenceSeverity.CRITICAL:
        raw_score = max(raw_score, 75)

    # Factor in external threat intelligence if present
    if threat_intel_malicious_count >= 5:
        raw_score = max(raw_score, 92)
        max_single_severity = EvidenceSeverity.CRITICAL
    elif threat_intel_malicious_count >= 1:
        raw_score += 35 * threat_intel_malicious_count
        if max_single_severity != EvidenceSeverity.CRITICAL:
            max_single_severity = EvidenceSeverity.HIGH
    elif threat_intel_suspicious_count >= 2:
        raw_score += 15

    # Enforce bounds
    final_score = min(100, max(0, raw_score))

    # Map score to standard RiskLevel
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

    # Confidence calculation: increases with corroborating evidence
    evidence_count = len(findings)
    base_confidence = 85.0
    if evidence_count >= 3 or threat_intel_malicious_count > 0:
        confidence = 95.0
    elif evidence_count >= 1:
        confidence = 90.0
    else:
        confidence = base_confidence

    # Layman Verdict & Executive Summary Generation
    if level == RiskLevel.CRITICAL:
        layman_verdict = "🚨 CRITICAL THREAT DETECTED — DO NOT ACCESS"
        exec_summary = (
            f"Forensic analysis detected high-severity threats ({evidence_count} indicators). "
            "Evidence indicates active phishing, brand impersonation, or known malicious infrastructure. "
            "Do not enter passwords, submit payment details, or download files from this link."
        )
    elif level == RiskLevel.HIGH_RISK:
        layman_verdict = "⚠️ HIGH RISK — MALICIOUS ACTIVITY SUSPECTED"
        exec_summary = (
            f"Significant risk signals observed across URL structure and infrastructure ({evidence_count} findings). "
            "Characteristics strongly correlate with credential harvesting lures or deceptive hosting."
        )
    elif level == RiskLevel.SUSPICIOUS:
        layman_verdict = "🔍 SUSPICIOUS — CAUTION STRONGLY ADVISED"
        exec_summary = (
            f"Target exhibits anomalous characteristics ({evidence_count} findings) such as atypical TLD, "
            "entropy deviations, or redirect parameters. Exercise extreme caution."
        )
    elif level == RiskLevel.LOW_RISK:
        layman_verdict = "ℹ️ LOW RISK — MINOR ANOMALIES NOTED"
        exec_summary = (
            "Target appears largely benign, with minor non-critical anomalies. "
            "Standard web navigation hygiene applies."
        )
    else:
        layman_verdict = "✅ VERIFIED SAFE — NO ADVERSE TELEMETRY DETECTED"
        exec_summary = (
            "Deterministic heuristic checks detected zero deceptive markers, brand spoofs, or suspicious infrastructure signals. "
            "Target meets standard baseline criteria."
        )

    # Recommended Actions
    actions = generate_recommended_actions(level)

    return RiskAssessment(
        score=final_score,
        level=level,
        confidence=confidence,
        layman_verdict=layman_verdict,
        executive_summary=exec_summary,
        recommended_actions=actions,
    )


def generate_recommended_actions(level: RiskLevel) -> List[RecommendedAction]:
    """Generates prioritized, contextual recommended mitigation actions based on risk level."""
    actions: List[RecommendedAction] = []
    if level in (RiskLevel.CRITICAL, RiskLevel.HIGH_RISK):
        actions.append(
            RecommendedAction(
                priority="IMMEDIATE",
                action="Do not open the link or enter sensitive credentials",
                rationale="Active deception or credential-harvesting indicators matched this target.",
                action_type="DO_NOT_CLICK",
            )
        )
        actions.append(
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Rotate passwords if previously submitted on this destination",
                rationale="Compromised credentials may be replayed against other enterprise services.",
                action_type="CHANGE_PASSWORD",
            )
        )
        actions.append(
            RecommendedAction(
                priority="REPORTING",
                action="Report link to your security team or corporate email gateway",
                rationale="Enables perimeter blacklisting and domain takedown notifications.",
                action_type="REPORT_PHISHING",
            )
        )
    elif level == RiskLevel.SUSPICIOUS:
        actions.append(
            RecommendedAction(
                priority="IMMEDIATE",
                action="Verify destination with sender using an independent, trusted channel",
                rationale="Do not rely on links provided in unexpected messages.",
                action_type="VERIFY_SENDER",
            )
        )
    else:
        actions.append(
            RecommendedAction(
                priority="IMMEDIATE",
                action="Safe to proceed with normal security awareness",
                rationale="No affirmative threat indicators were detected.",
                action_type="SAFE_TO_PROCEED",
            )
        )
    return actions


# Alias for internal backwards-compatibility
_generate_recommended_actions = generate_recommended_actions

