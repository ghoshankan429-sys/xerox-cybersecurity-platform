import uuid
import pytest
from httpx import AsyncClient
from app.core.config import Settings
from app.cache.redis_client import check_redis_health


def test_database_url_normalization():
    """Verify that postgres:// and postgresql:// are normalized to postgresql+asyncpg://."""
    s1 = Settings(DATABASE_URL="postgres://user:pass@ep-cool-db.us-east-2.aws.neon.tech/xerox_db")
    assert s1.DATABASE_URL.startswith("postgresql+asyncpg://")

    s2 = Settings(DATABASE_URL="postgresql://user:pass@containers-us-west.railway.app:5432/railway")
    assert s2.DATABASE_URL.startswith("postgresql+asyncpg://")

    s3 = Settings(DATABASE_URL="sqlite+aiosqlite:///./test.db")
    assert s3.DATABASE_URL == "sqlite+aiosqlite:///./test.db"


@pytest.mark.asyncio
async def test_dual_auth_via_bearer_token(async_client: AsyncClient):
    """Verify that an API client can authenticate using Authorization: Bearer <session_token> without cookies."""
    email = f"bearer_{uuid.uuid4().hex[:8]}@xerox.sec"
    pwd = "StrongPassword123!"

    # 1. Register
    reg = await async_client.post("/api/v1/auth/register", json={"email": email, "password": pwd})
    assert reg.status_code == 201

    # 2. Login and extract session_token
    login = await async_client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert login.status_code == 200
    token = login.json().get("session_token")
    assert token is not None and len(token) > 16

    # 3. Create a clean client with NO cookies
    from httpx import ASGITransport, AsyncClient as CleanClient
    from app.main import app

    async with CleanClient(transport=ASGITransport(app=app), base_url="http://test") as headless_client:
        # Access /auth/me without header -> 401
        unauth = await headless_client.get("/api/v1/auth/me")
        assert unauth.status_code == 401

        # Access with Authorization: Bearer header -> 200
        auth_header_resp = await headless_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert auth_header_resp.status_code == 200
        assert auth_header_resp.json()["email"] == email

        # Access with X-Session-Token custom header -> 200
        x_token_resp = await headless_client.get(
            "/api/v1/auth/me",
            headers={"X-Session-Token": token},
        )
        assert x_token_resp.status_code == 200
        assert x_token_resp.json()["email"] == email


@pytest.mark.asyncio
async def test_redis_health_probe():
    """Verify check_redis_health returns structured status dictionary."""
    res = await check_redis_health()
    assert "status" in res
    assert res["status"] in ("connected", "bypassed", "degraded", "unreachable")
