from dataclasses import dataclass
from typing import List
from app.schemas.threat import (
    RiskLevel,
    EvidenceItem,
    EvidenceCategory,
    EvidenceSeverity,
    RecommendedAction,
)
from app.analyzers.screenshot.engine import ScreenshotHeuristicResult


SEVERITY_WEIGHTS = {
    EvidenceSeverity.CRITICAL: 50,
    EvidenceSeverity.HIGH: 25,
    EvidenceSeverity.MEDIUM: 12,
    EvidenceSeverity.LOW: 5,
    EvidenceSeverity.INFO: 0,
}


@dataclass(frozen=True)
class ScreenshotRiskAssessment:
    risk_score: int
    risk_level: RiskLevel
    confidence_score: float
    layman_verdict: str
    executive_summary: str
    recommended_actions: List[RecommendedAction]
    all_findings: List[EvidenceItem]


def calculate_screenshot_risk_score(
    screenshot_result: ScreenshotHeuristicResult,
    message_findings: List[EvidenceItem],
    url_findings: List[EvidenceItem],
    has_high_risk_url: bool,
    max_url_score: int,
    detected_brands: List[str],
) -> ScreenshotRiskAssessment:
    """Calculates risk score (0-100) combining screenshot visual heuristics,
    M6 message heuristics on OCR text, and M5 URL security findings.
    """
    all_findings: List[EvidenceItem] = []
    seen_titles = set()

    # Aggregate findings avoiding duplicate titles
    for finding in screenshot_result.findings + message_findings + url_findings:
        if finding.title not in seen_titles:
            seen_titles.add(finding.title)
            all_findings.append(finding)

    # 1. Base Score from Findings
    raw_score = 0
    for finding in all_findings:
        raw_score += SEVERITY_WEIGHTS.get(finding.severity, 0)

    # Incorporate worst URL score if applicable
    if max_url_score > 0:
        raw_score = max(raw_score, int(max_url_score * 0.85))

    # 2. Cross-Correlation Amplifiers
    # A. Visual Login Form paired with High-Risk URL or Credential Harvesting
    if screenshot_result.has_login_form and (has_high_risk_url or screenshot_result.has_credential_harvesting):
        corr_finding = EvidenceItem(
            category=EvidenceCategory.IDENTITY,
            severity=EvidenceSeverity.CRITICAL,
            title="Deceptive Visual Login Portal Paired with Hostile Infrastructure",
            description="The screenshot displays an interactive authentication form paired with high-risk web hosting or active credential theft cues.",
            technical_proof=f"Visual login form: True, High-risk URL: {has_high_risk_url}, Credential demand: {screenshot_result.has_credential_harvesting}",
            why_this_matters="This signature is characteristic of credential harvester attack sites designed to harvest session tokens and passwords.",
        )
        if corr_finding.title not in seen_titles:
            seen_titles.add(corr_finding.title)
            all_findings.append(corr_finding)
        raw_score = max(raw_score, 88)

    # B. Brand Spoofing paired with Login Form
    if screenshot_result.has_brand_spoofing and screenshot_result.has_login_form:
        raw_score = max(raw_score, 82)

    # C. Counterfeit Alert (Tech Support Scam)
    if screenshot_result.has_counterfeit_alert:
        raw_score = max(raw_score, 75)

    # Clamp score to 0..100
    final_score = min(max(raw_score, 0), 100)

    # 3. Map to RiskLevel
    if final_score >= 85:
        risk_level = RiskLevel.CRITICAL
    elif final_score >= 65:
        risk_level = RiskLevel.HIGH_RISK
    elif final_score >= 35:
        risk_level = RiskLevel.SUSPICIOUS
    elif final_score >= 15:
        risk_level = RiskLevel.LOW_RISK
    else:
        risk_level = RiskLevel.BENIGN

    # Confidence calculation
    num_indicators = len(all_findings)
    base_confidence = 80.0
    if num_indicators >= 3:
        base_confidence = 94.0
    elif num_indicators >= 1:
        base_confidence = 88.0
    confidence_score = min(base_confidence, 99.0)

    # 4. Generate Layman Verdict & Executive Summary
    brand_context = f" targeting {', '.join(detected_brands)}" if detected_brands else ""

    if risk_level == RiskLevel.CRITICAL:
        layman_verdict = f"Critical Threat: Malicious Credential Portal or Visual Trap{brand_context}"
        executive_summary = (
            f"Optical analysis confirmed a high-confidence deceptive interface{brand_context}. "
            "The visual frame contains authentication prompts, sensitive credential requests, or counterfeit alerts "
            "paired with untrusted infrastructure designed to compromise account credentials."
        )
    elif risk_level == RiskLevel.HIGH_RISK:
        layman_verdict = f"High Risk: Suspect Brand Portal or Phishing Lure{brand_context}"
        executive_summary = (
            f"The screenshot exhibits strong indicators of brand impersonation or coercive social engineering{brand_context}. "
            "Visual elements match known phishing templates or tech support lures."
        )
    elif risk_level == RiskLevel.SUSPICIOUS:
        layman_verdict = "Suspicious Visual Content: Potential Phishing or Misleading Elements"
        executive_summary = (
            "The screenshot exhibits abnormal urgency, unverified domains, or unconventional layout structures. "
            "Exercise caution before interacting with any instructions shown."
        )
    elif risk_level == RiskLevel.LOW_RISK:
        layman_verdict = "Low Risk: Minor Visual Anomalies"
        executive_summary = (
            "The image shows standard interface elements with minor non-standard attributes. "
            "No immediate credential theft mechanisms were identified."
        )
    else:
        layman_verdict = "Verified Benign Visual Capture"
        executive_summary = (
            "Analysis identified standard visual content with no deceptive branding, credential forms, "
            "fake alerts, or hostile web addresses."
        )

    # 5. Prioritized Recommended Actions
    actions: List[RecommendedAction] = []
    if risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH_RISK):
        if screenshot_result.has_login_form:
            actions.append(
                RecommendedAction(
                    priority="IMMEDIATE",
                    action="Do not enter passwords or personal credentials into this portal",
                    rationale="The interface is counterfeit and will transmit entered credentials directly to adversaries.",
                    action_type="DO_NOT_CLICK",
                )
            )
        if screenshot_result.has_payment_or_qr:
            actions.append(
                RecommendedAction(
                    priority="IMMEDIATE",
                    action="Do not scan the QR code or transfer funds",
                    rationale="QR codes and crypto payment requests in unverified frames are non-reversible fraud vectors.",
                    action_type="DO_NOT_CLICK",
                )
            )
        if screenshot_result.has_counterfeit_alert:
            actions.append(
                RecommendedAction(
                    priority="IMMEDIATE",
                    action="Do not call the phone number displayed on screen",
                    rationale="The security warning is simulated; the number connects to a fraudulent tech support operation.",
                    action_type="DO_NOT_CLICK",
                )
            )
        actions.append(
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Close the corresponding browser tab and report the site",
                rationale="Prevents accidental form submission or ongoing exposure to the lure.",
                action_type="REPORT_PHISHING",
            )
        )
    elif risk_level == RiskLevel.SUSPICIOUS:
        actions.append(
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Verify authenticity through official company bookmarks",
                rationale="Avoid accessing sensitive portals from unverified links or screenshots.",
                action_type="VERIFY_SENDER",
            )
        )
    else:
        actions.append(
            RecommendedAction(
                priority="PREVENTATIVE",
                action="Safe to proceed with normal caution",
                rationale="No deceptive visual or network indicators detected.",
                action_type="SAFE_TO_PROCEED",
            )
        )

    return ScreenshotRiskAssessment(
        risk_score=final_score,
        risk_level=risk_level,
        confidence_score=confidence_score,
        layman_verdict=layman_verdict,
        executive_summary=executive_summary,
        recommended_actions=actions,
        all_findings=all_findings,
    )
