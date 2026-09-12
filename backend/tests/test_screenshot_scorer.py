import pytest
from app.schemas.threat import RiskLevel, EvidenceItem, EvidenceCategory, EvidenceSeverity
from app.analyzers.screenshot.engine import ScreenshotHeuristicResult
from app.analyzers.screenshot.scorer import calculate_screenshot_risk_score


def test_benign_screenshot_scoring():
    screenshot_res = ScreenshotHeuristicResult()
    assessment = calculate_screenshot_risk_score(
        screenshot_result=screenshot_res,
        message_findings=[],
        url_findings=[],
        has_high_risk_url=False,
        max_url_score=0,
        detected_brands=[],
    )
    assert assessment.risk_level == RiskLevel.BENIGN
    assert assessment.risk_score < 15
    assert "Verified Benign" in assessment.layman_verdict
    assert any(a.action_type == "SAFE_TO_PROCEED" for a in assessment.recommended_actions)


def test_login_form_with_high_risk_url_cross_correlation():
    finding = EvidenceItem(
        category=EvidenceCategory.CONTENT,
        severity=EvidenceSeverity.HIGH,
        title="Suspicious Visual Authentication / Login Interface",
        description="Login form detected.",
        technical_proof="Form",
        why_this_matters="Phishing risk",
    )
    screenshot_res = ScreenshotHeuristicResult(
        findings=[finding],
        has_login_form=True,
    )
    assessment = calculate_screenshot_risk_score(
        screenshot_result=screenshot_res,
        message_findings=[],
        url_findings=[],
        has_high_risk_url=True,
        max_url_score=85,
        detected_brands=["Apple"],
    )
    assert assessment.risk_level in (RiskLevel.HIGH_RISK, RiskLevel.CRITICAL)
    assert assessment.risk_score >= 80
    assert any("Deceptive Visual Login Portal Paired with Hostile Infrastructure" in f.title for f in assessment.all_findings)
    assert any(a.action_type == "DO_NOT_CLICK" for a in assessment.recommended_actions)


def test_credential_harvesting_escalates_to_critical():
    finding = EvidenceItem(
        category=EvidenceCategory.IDENTITY,
        severity=EvidenceSeverity.CRITICAL,
        title="High-Value Secret & Credential Solicitation",
        description="Seed phrase requested.",
        technical_proof="seed phrase",
        why_this_matters="Irreversible theft",
    )
    screenshot_res = ScreenshotHeuristicResult(
        findings=[finding],
        has_login_form=True,
        has_credential_harvesting=True,
    )
    assessment = calculate_screenshot_risk_score(
        screenshot_result=screenshot_res,
        message_findings=[],
        url_findings=[],
        has_high_risk_url=False,
        max_url_score=0,
        detected_brands=["MetaMask"],
    )
    assert assessment.risk_level == RiskLevel.CRITICAL
    assert assessment.risk_score >= 85
    assert "Critical Threat" in assessment.layman_verdict
