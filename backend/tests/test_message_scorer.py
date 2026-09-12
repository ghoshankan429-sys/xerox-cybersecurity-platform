import pytest
from app.analyzers.message.scorer import calculate_message_risk_score
from app.schemas.threat import (
    RiskLevel,
    EvidenceItem,
    EvidenceCategory,
    EvidenceSeverity,
)


def test_benign_scoring_and_verdict():
    """Empty findings produce low/benign risk score."""
    assessment = calculate_message_risk_score(
        message_findings=[],
        url_findings=[],
        url_max_score=0,
        has_correlation=False,
    )
    assert assessment.score <= 15
    assert assessment.level == RiskLevel.BENIGN
    assert "VERIFIED BENIGN" in assessment.layman_verdict
    assert any(a.action_type == "SAFE_TO_PROCEED" for a in assessment.recommended_actions)


def test_high_risk_scoring_with_credentials_and_urgency():
    """Combining critical/high social engineering findings elevates score into HIGH_RISK or CRITICAL."""
    msg_findings = [
        EvidenceItem(
            category=EvidenceCategory.IDENTITY,
            severity=EvidenceSeverity.HIGH,
            title="Direct Password / PIN Harvesting Request",
            description="Demands user password.",
            technical_proof="Password keyword",
            why_this_matters="Credential theft.",
        ),
        EvidenceItem(
            category=EvidenceCategory.CONTENT,
            severity=EvidenceSeverity.HIGH,
            title="Account Suspension Threat",
            description="Threatens closure in 24 hours.",
            technical_proof="Suspension keyword",
            why_this_matters="Panic induction.",
        ),
    ]

    assessment = calculate_message_risk_score(
        message_findings=msg_findings,
        url_findings=[],
        url_max_score=0,
        has_correlation=False,
    )
    assert assessment.score >= 50
    assert assessment.level in (RiskLevel.SUSPICIOUS, RiskLevel.HIGH_RISK)


def test_cross_correlation_amplification():
    """Social engineering paired with a high-risk URL elevates verdict to CRITICAL."""
    msg_findings = [
        EvidenceItem(
            category=EvidenceCategory.CONTENT,
            severity=EvidenceSeverity.HIGH,
            title="Account Suspension Threat",
            description="Threatens closure in 12 hours.",
            technical_proof="Urgent trigger",
            why_this_matters="Panic induction.",
        )
    ]
    url_findings = [
        EvidenceItem(
            category=EvidenceCategory.IDENTITY,
            severity=EvidenceSeverity.CRITICAL,
            title="Brand Impersonation in URL",
            description="Domain mimics Chase bank.",
            technical_proof="chase-security-login.xyz",
            why_this_matters="Phishing.",
        )
    ]

    assessment = calculate_message_risk_score(
        message_findings=msg_findings,
        url_findings=url_findings,
        url_max_score=85,
        has_correlation=True,
    )
    assert assessment.score >= 85
    assert assessment.level in (RiskLevel.HIGH_RISK, RiskLevel.CRITICAL)
    assert any(a.action_type == "DO_NOT_CLICK" for a in assessment.recommended_actions)
