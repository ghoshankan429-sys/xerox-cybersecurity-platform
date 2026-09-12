import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone
from app.core.datetime_utils import get_monotonic_utc_now
from app.core.config import settings
from app.schemas.threat import ThreatReport, TargetType, RiskLevel
from app.api.v1.scans import SCAN_DATABASE, SCAN_ORDER, get_scan_history


def test_monotonic_timestamp_strictly_increasing():
    """Verify that 1000 consecutive calls to get_monotonic_utc_now return strictly increasing datetimes."""
    timestamps = [get_monotonic_utc_now() for _ in range(1000)]
    for i in range(1, len(timestamps)):
        assert timestamps[i] > timestamps[i - 1], f"Timestamp collision at index {i}: {timestamps[i]} not > {timestamps[i-1]}"


@pytest.mark.asyncio
async def test_scans_in_memory_history_tie_breaking():
    """Verify in-memory scan history uses insertion order when analyzed_at matches."""
    same_time = "2026-09-12T12:00:00Z"
    id_first = f"test-tie-{uuid.uuid4().hex[:6]}-1"
    id_second = f"test-tie-{uuid.uuid4().hex[:6]}-2"

    global SCAN_DATABASE, SCAN_ORDER
    # Insert first
    order1 = 99990
    SCAN_ORDER[id_first] = order1
    SCAN_DATABASE[id_first] = ThreatReport(
        scan_id=id_first,
        target_type=TargetType.URL,
        raw_target="https://tie-test-1.com",
        defanged_target="hxxps://tie-test-1[.]com",
        risk_score=10,
        risk_level=RiskLevel.BENIGN,
        confidence_score=0.9,
        executive_summary="Tie test 1",
        layman_verdict="Tie test 1 verdict",
        evidence_items=[],
        recommended_actions=[],
        technical_metadata={},
        analyzed_at=same_time,
    )

    # Insert second (later order, same timestamp)
    order2 = 99991
    SCAN_ORDER[id_second] = order2
    SCAN_DATABASE[id_second] = ThreatReport(
        scan_id=id_second,
        target_type=TargetType.URL,
        raw_target="https://tie-test-2.com",
        defanged_target="hxxps://tie-test-2[.]com",
        risk_score=20,
        risk_level=RiskLevel.BENIGN,
        confidence_score=0.9,
        executive_summary="Tie test 2",
        layman_verdict="Tie test 2 verdict",
        evidence_items=[],
        recommended_actions=[],
        technical_metadata={},
        analyzed_at=same_time,
    )

    history = await get_scan_history(limit=50)
    history_ids = [item.scan_id for item in history]
    assert id_second in history_ids
    assert id_first in history_ids
    assert history_ids.index(id_second) < history_ids.index(id_first)


@pytest.mark.asyncio
async def test_rapid_scans_db_history_ordering(async_client: AsyncClient):
    """Verify rapid consecutive URL scans always return newest first in /analyze/history."""
    email = f"rapid_{uuid.uuid4().hex[:8]}@xerox.sec"
    pwd = "StrongPassword123!"

    reg = await async_client.post(f"{settings.API_V1_STR}/auth/register", json={"email": email, "password": pwd})
    assert reg.status_code == 201
    login = await async_client.post(f"{settings.API_V1_STR}/auth/login", json={"email": email, "password": pwd})
    assert login.status_code == 200

    # Rapid sequential scans
    scan_ids = []
    for i in range(3):
        res = await async_client.post(
            f"{settings.API_V1_STR}/analyze/url",
            json={"url": f"https://rapid-scan-test-{i}.org"},
        )
        assert res.status_code == 200
        scan_ids.append(res.json()["scan_id"])

    # History must have newest first: [scan_ids[2], scan_ids[1], scan_ids[0]]
    hist_resp = await async_client.get(f"{settings.API_V1_STR}/analyze/history?limit=10")
    assert hist_resp.status_code == 200
    returned_history = hist_resp.json()

    returned_ids = [item["scan_id"] for item in returned_history[:3]]
    assert returned_ids == [scan_ids[2], scan_ids[1], scan_ids[0]], f"Expected {[scan_ids[2], scan_ids[1], scan_ids[0]]}, got {returned_ids}"
