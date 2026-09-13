import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.models.feedback import Feedback


async def create_user(async_client: AsyncClient, prefix: str = "analyst"):
    email = f"{prefix}_{uuid.uuid4().hex[:8]}@xerox.sec"
    pwd = "StrongPassword123!"
    reg = await async_client.post(f"{settings.API_V1_STR}/auth/register", json={"email": email, "password": pwd})
    assert reg.status_code == 201
    login = await async_client.post(f"{settings.API_V1_STR}/auth/login", json={"email": email, "password": pwd})
    assert login.status_code == 200
    return email, pwd


@pytest.mark.asyncio
async def test_unauthenticated_feedback_rejected(async_client: AsyncClient):
    """Submitting feedback without authentication returns 401."""
    res = await async_client.post(
        f"{settings.API_V1_STR}/feedback",
        json={"scan_id": str(uuid.uuid4()), "feedback": "Great analysis."},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_submit_and_retrieve_feedback_flow(async_client: AsyncClient):
    """Authenticated user submits feedback on their scan and retrieves it."""
    await create_user(async_client, "feedback_user")

    # 1. Perform scan
    scan_resp = await async_client.post(
        f"{settings.API_V1_STR}/analyze/url",
        json={"url": "https://feedback-target-test.org"},
    )
    assert scan_resp.status_code == 200
    scan_id = scan_resp.json()["scan_id"]

    # 2. Submit feedback
    fb_text = "Accurately flagged suspicious high-entropy parameters."
    fb_resp = await async_client.post(
        f"{settings.API_V1_STR}/feedback",
        json={"scan_id": scan_id, "feedback": fb_text, "rating": 5},
    )
    assert fb_resp.status_code == 201
    fb_data = fb_resp.json()
    assert fb_data["scan_id"] == scan_id
    assert fb_data["feedback"] == fb_text
    assert "id" in fb_data

    # 3. Verify DB persistence
    async with AsyncSessionLocal() as db:
        stmt = select(Feedback).where(Feedback.id == uuid.UUID(fb_data["id"]))
        entry = (await db.execute(stmt)).scalar_one_or_none()
        assert entry is not None
        assert entry.feedback == fb_text

    # 4. Retrieve feedback list
    list_resp = await async_client.get(f"{settings.API_V1_STR}/feedback")
    assert list_resp.status_code == 200
    entries = list_resp.json()
    assert len(entries) >= 1
    assert any(e["id"] == fb_data["id"] for e in entries)


@pytest.mark.asyncio
async def test_feedback_tenant_isolation(async_client: AsyncClient):
    """User B cannot submit feedback on User A's scan report."""
    # User A creates a scan
    await create_user(async_client, "user_a")
    scan_resp_a = await async_client.post(
        f"{settings.API_V1_STR}/analyze/url",
        json={"url": "https://user-a-exclusive.com"},
    )
    scan_id_a = scan_resp_a.json()["scan_id"]

    # User B logs in
    await create_user(async_client, "user_b")

    # User B attempts to submit feedback for User A's scan
    res_b = await async_client.post(
        f"{settings.API_V1_STR}/feedback",
        json={"scan_id": scan_id_a, "feedback": "Attempting cross-tenant feedback injection"},
    )
    assert res_b.status_code == 403

    # Feedback for completely non-existent scan ID returns 404
    res_nonexistent = await async_client.post(
        f"{settings.API_V1_STR}/feedback",
        json={"scan_id": str(uuid.uuid4()), "feedback": "Ghost scan feedback"},
    )
    assert res_nonexistent.status_code == 404
