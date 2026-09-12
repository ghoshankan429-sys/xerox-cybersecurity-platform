import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == "XEROX"
    assert data["status"] == "OPERATIONAL"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoints(async_client):
    res_alias = await async_client.get("/api/health")
    assert res_alias.status_code == 200
    assert res_alias.json()["status"] == "healthy"

    res_v1 = await async_client.get(f"{settings.API_V1_STR}/health")
    assert res_v1.status_code == 200
    data = res_v1.json()
    assert data["status"] == "healthy"
    assert data["service"] == "XEROX Autonomous Cybersecurity Engine"


def test_package_structure_and_imports():
    """Verify all required backend modules import cleanly."""
    import app.api
    import app.core
    import app.models
    import app.schemas
    import app.services
    import app.security
    import app.analyzers
    import app.threat_intel
    import app.ai
    import app.cache
    import app.database
    import app.workers

    assert app.core.config.settings.PROJECT_NAME == "XEROX"
