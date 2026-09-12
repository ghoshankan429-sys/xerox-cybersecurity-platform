import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.base import Base
from app.database.session import engine


@pytest.fixture(autouse=True)
async def ensure_database_tables():
    """Ensure all database schema tables exist before executing each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
