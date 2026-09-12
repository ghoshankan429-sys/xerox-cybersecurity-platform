from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from app.schemas.threat import (
    URLScanRequest,
    MessageScanRequest,
    ThreatReport,
    ScanHistoryItem,
    StatsSummary,
    TargetType,
    RiskLevel,
)
from app.engines.url_analyzer import analyze_url_target, defang_url
from app.engines.message_analyzer import analyze_message_content
from app.engines.ai_analyst import synthesize_threat_report

router = APIRouter(prefix="/scans", tags=["scans"])

# In-memory investigation archive (persists during server lifetime)
SCAN_DATABASE: dict[str, ThreatReport] = {}
SCAN_ORDER: dict[str, int] = {}
_scan_counter: int = 0

# Seed initial demonstration history so dashboard and archive look populated on startup
def _seed_initial_history():
    demo_samples = [
        ThreatReport(
            scan_id="demo-apple-phish-001",
            target_type=TargetType.URL,
            raw_target="https://apple-id-verify.support-secure.live/auth",
            defanged_target="hxxps://apple-id-verify[.]support-secure[.]live/auth",
            risk_score=96,
            risk_level=RiskLevel.CRITICAL,
            confidence_score=0.96,
            executive_summary="Active credential harvesting campaign impersonating Apple ID. Domain registered 48 hours ago in an unverified TLD with a cloned login interface.",
            layman_verdict="🚨 DO NOT CLICK OR ENTER DETAILS: This is NOT Apple. It is a fraudulent clone engineered to steal your Apple ID password and 2FA codes.",
            evidence_items=[],
            recommended_actions=[],
            technical_metadata={
                "domain": "apple-id-verify.support-secure.live",
                "registered_domain": "support-secure.live",
                "tld": "live",
                "ip_addresses": ["185.220.101.5"],
                "entropy": 3.4,
                "detected_brands": ["apple"],
                "extracted_urls": ["hxxps://apple-id-verify[.]support-secure[.]live/auth"]
            },
            analyzed_at="2026-09-12T08:15:00Z"
        ),
        ThreatReport(
            scan_id="demo-sms-urgent-002",
            target_type=TargetType.MESSAGE,
            raw_target="USPS Alert: Your package has an unpaid customs charge of $2.49. Delivery will be cancelled within 12 hours: hxxps://usps-redelivery-support[.]xyz",
            defanged_target="USPS Alert: Your package has an unpaid customs charge of $2.49. Delivery will be cancelled within 12 hours: hxxps://usps-redelivery-support[.]xyz",
            risk_score=88,
            risk_level=RiskLevel.HIGH_RISK,
            confidence_score=0.92,
            executive_summary="Postal delivery smishing lure utilizing artificial time urgency to force immediate credit card payment on a spoofed portal.",
            layman_verdict="⚠️ FAKE DELIVERY SCAM: The postal service does not send payment ultimatums via random text messages. Do not pay.",
            evidence_items=[],
            recommended_actions=[],
            technical_metadata={
                "domain": "usps-redelivery-support.xyz",
                "registered_domain": "usps-redelivery-support.xyz",
                "tld": "xyz",
                "ip_addresses": ["45.142.214.10"],
                "entropy": 3.6,
                "detected_brands": ["usps"],
                "extracted_urls": ["hxxps://usps-redelivery-support[.]xyz"]
            },
            analyzed_at="2026-09-12T09:30:00Z"
        ),
        ThreatReport(
            scan_id="demo-safe-github-003",
            target_type=TargetType.URL,
            raw_target="https://github.com",
            defanged_target="hxxps://github[.]com",
            risk_score=6,
            risk_level=RiskLevel.BENIGN,
            confidence_score=0.98,
            executive_summary="Verified legitimate corporate infrastructure. Long-standing domain history, high-reputation nameservers, valid DigiCert TLS certificate.",
            layman_verdict="✅ VERIFIED SAFE: Official GitHub portal. No deceptive behaviors or malicious telemetry detected.",
            evidence_items=[],
            recommended_actions=[],
            technical_metadata={
                "domain": "github.com",
                "registered_domain": "github.com",
                "tld": "com",
                "ip_addresses": ["140.82.121.4"],
                "entropy": 2.1,
                "detected_brands": [],
                "extracted_urls": ["hxxps://github[.]com"]
            },
            analyzed_at="2026-09-12T10:00:00Z"
        )
    ]
    global _scan_counter
    for sample in demo_samples:
        _scan_counter += 1
        SCAN_DATABASE[sample.scan_id] = sample
        SCAN_ORDER[sample.scan_id] = _scan_counter

_seed_initial_history()

@router.post("/url", response_model=ThreatReport)
async def scan_url_endpoint(req: URLScanRequest):
    if not req.url or len(req.url.strip()) < 3:
        raise HTTPException(status_code=400, detail="A valid URL or domain is required.")
    
    raw = req.url.strip()
    defanged = defang_url(raw)
    
    # Analyze
    metadata, evidence_items, detected_brands = await analyze_url_target(raw)
    
    # Synthesize
    report = await synthesize_threat_report(
        target_type=TargetType.URL,
        raw_target=raw,
        defanged_target=defanged,
        metadata=metadata,
        evidence_items=evidence_items,
    )

    global _scan_counter
    _scan_counter += 1
    SCAN_DATABASE[report.scan_id] = report
    SCAN_ORDER[report.scan_id] = _scan_counter
    return report

@router.post("/message", response_model=ThreatReport)
async def scan_message_endpoint(req: MessageScanRequest):
    if not req.content or len(req.content.strip()) < 3:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")
    
    raw = req.content.strip()
    defanged = defang_url(raw)

    metadata, evidence_items, extracted_urls = await analyze_message_content(
        raw, sender_metadata=req.sender_metadata
    )

    report = await synthesize_threat_report(
        target_type=TargetType.MESSAGE,
        raw_target=raw,
        defanged_target=defanged,
        metadata=metadata,
        evidence_items=evidence_items,
    )

    global _scan_counter
    _scan_counter += 1
    SCAN_DATABASE[report.scan_id] = report
    SCAN_ORDER[report.scan_id] = _scan_counter
    return report

@router.get("/history", response_model=list[ScanHistoryItem])
async def get_scan_history(limit: int = Query(50, ge=1, le=200)):
    items: list[ScanHistoryItem] = []
    # Sort descending by analyzed_at with insertion order as deterministic tie-breaker
    sorted_reports = sorted(
        SCAN_DATABASE.values(),
        key=lambda r: (r.analyzed_at, SCAN_ORDER.get(r.scan_id, 0)),
        reverse=True,
    )

    for r in sorted_reports[:limit]:
        items.append(
            ScanHistoryItem(
                scan_id=r.scan_id,
                target_type=r.target_type,
                defanged_target=r.defanged_target[:120],
                risk_level=r.risk_level,
                risk_score=r.risk_score,
                analyzed_at=r.analyzed_at,
                executive_summary=r.executive_summary,
            )
        )
    return items

@router.get("/{scan_id}", response_model=ThreatReport)
async def get_scan_report(scan_id: str):
    report = SCAN_DATABASE.get(scan_id)
    if not report:
        raise HTTPException(status_code=404, detail="Investigation report not found.")
    return report

@router.get("/summary/stats", response_model=StatsSummary)
async def get_stats():
    total = len(SCAN_DATABASE)
    threats_blocked = sum(1 for r in SCAN_DATABASE.values() if r.risk_level in (RiskLevel.HIGH_RISK, RiskLevel.CRITICAL))
    benign = sum(1 for r in SCAN_DATABASE.values() if r.risk_level == RiskLevel.BENIGN)
    suspicious = sum(1 for r in SCAN_DATABASE.values() if r.risk_level in (RiskLevel.LOW_RISK, RiskLevel.SUSPICIOUS))
    
    types_count: dict[str, int] = {}
    for r in SCAN_DATABASE.values():
        types_count[r.target_type.value] = types_count.get(r.target_type.value, 0) + 1

    return StatsSummary(
        total_scans=total,
        threats_blocked=threats_blocked,
        benign_verified=benign,
        suspicious_flagged=suspicious,
        scans_by_type=types_count,
    )
