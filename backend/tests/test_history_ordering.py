import uuid
import pytest
from httpx import AsyncClient
from app.core.datetime_utils import get_monotonic_utc_now
from app.core.config import settings


def test_monotonic_timestamp_strictly_increasing():
    """Verify that 1000 consecutive calls to get_monotonic_utc_now return strictly increasing datetimes."""
    timestamps = [get_monotonic_utc_now() for _ in range(1000)]
    for i in range(1, len(timestamps)):
        assert timestamps[i] > timestamps[i - 1], f"Timestamp collision at index {i}: {timestamps[i]} not > {timestamps[i-1]}"


@pytest.mark.asyncio
async def test_scans_alias_history_ordering(async_client: AsyncClient):
    """Verify /scans/history alias returns database scans in strictly newest-first order."""
    email = f"alias_{uuid.uuid4().hex[:8]}@xerox.sec"
    pwd = "StrongPassword123!"

    reg = await async_client.post(f"{settings.API_V1_STR}/auth/register", json={"email": email, "password": pwd})
    assert reg.status_code == 201
    login = await async_client.post(f"{settings.API_V1_STR}/auth/login", json={"email": email, "password": pwd})
    assert login.status_code == 200

    # Submit 2 scans via /scans/url
    res1 = await async_client.post(f"{settings.API_V1_STR}/scans/url", json={"url": "https://alias-test-one.com"})
    assert res1.status_code == 200
    scan_id1 = res1.json()["scan_id"]

    res2 = await async_client.post(f"{settings.API_V1_STR}/scans/url", json={"url": "https://alias-test-two.com"})
    assert res2.status_code == 200
    scan_id2 = res2.json()["scan_id"]

    # History via /scans/history must return scan_id2 first
    hist_resp = await async_client.get(f"{settings.API_V1_STR}/scans/history?limit=10")
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) >= 2
    assert history[0]["scan_id"] == scan_id2
    assert history[1]["scan_id"] == scan_id1


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
