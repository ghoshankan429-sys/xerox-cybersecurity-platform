import asyncio
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.engines.url_analyzer import analyze_url_target
from app.engines.message_analyzer import analyze_message_content
from app.engines.ai_analyst import synthesize_threat_report
from app.schemas.threat import TargetType, RiskLevel

async def test_apple_phishing_url():
    url = "https://apple-id-verify.support-secure.live/auth"
    meta, evidence, brands = await analyze_url_target(url)
    report = await synthesize_threat_report(
        TargetType.URL, url, url.replace(".", "[.]"), meta, evidence
    )
    print(f"URL: {url}")
    print(f"Risk Score: {report.risk_score} | Level: {report.risk_level.value}")
    print(f"Evidence Count: {len(report.evidence_items)}")
    print(f"Layman Verdict: {report.layman_verdict}")
    assert report.risk_level in (RiskLevel.HIGH_RISK, RiskLevel.CRITICAL)
    assert "apple" in report.technical_metadata.detected_brands

async def test_benign_url():
    url = "https://google.com"
    meta, evidence, brands = await analyze_url_target(url)
    report = await synthesize_threat_report(
        TargetType.URL, url, url.replace(".", "[.]"), meta, evidence
    )
    print(f"\nURL: {url}")
    print(f"Risk Score: {report.risk_score} | Level: {report.risk_level.value}")
    print(f"Risk Level: {report.risk_level.value}")
    assert report.risk_level in (RiskLevel.BENIGN, RiskLevel.LOW_RISK)

async def test_smishing_message():
    msg = "URGENT NOTICE: Your Chase bank account is suspended due to unauthorized activity. Verify identity within 12 hours: hxxps://chase-security-login[.]xyz"
    meta, evidence, urls = await analyze_message_content(msg, sender_metadata="+18005550199")
    report = await synthesize_threat_report(
        TargetType.MESSAGE, msg, msg, meta, evidence
    )
    print(f"\nMessage: {msg}")
    print(f"Risk Score: {report.risk_score} | Level: {report.risk_level.value}")
    print(f"Social Engineering Flags: {report.technical_metadata.social_engineering_flags}")
    print(f"Layman: {report.layman_verdict}")
    assert report.risk_level in (RiskLevel.HIGH_RISK, RiskLevel.CRITICAL)

async def main():
    print("Running Xerox Forensic Engine Tests...")
    await test_apple_phishing_url()
    await test_benign_url()
    await test_smishing_message()
    print("\nALL ENGINE TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(main())
