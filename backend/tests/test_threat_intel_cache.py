import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.threat_intel.schemas import ThreatIntelResult, ThreatIntelStatus
from app.threat_intel.virustotal import VirusTotalProvider
from app.cache.redis_client import ThreatIntelCache


@pytest.mark.asyncio
async def test_virustotal_unconfigured_api_key():
    """VirusTotal returns NOT_CONFIGURED gracefully if API key is missing."""
    provider = VirusTotalProvider(api_key="")
    result = await provider.lookup_url("https://example.com")
    assert result.status == ThreatIntelStatus.NOT_CONFIGURED
    assert result.malicious_count == 0
    assert "VirusTotal" in result.provider_name


@pytest.mark.asyncio
async def test_virustotal_successful_lookup():
    """Parses successful VirusTotal v3 URL analysis response."""
    provider = VirusTotalProvider(api_key="test_dummy_key")

    mock_resp = {
        "data": {
            "attributes": {
                "last_analysis_stats": {
                    "malicious": 5,
                    "suspicious": 1,
                    "harmless": 65,
                    "undetected": 10,
                },
                "categories": {},
                "reputation": -45,
            }
        }
    }

    mock_response = httpx.Response(200, json=mock_resp, request=httpx.Request("GET", "https://test"))

    with patch.object(httpx.AsyncClient, "get", return_value=mock_response):
        result = await provider.lookup_url("https://malicious-phish.top")
        assert result.status == ThreatIntelStatus.MALICIOUS
        assert result.malicious_count == 5
        assert result.suspicious_count == 1
        assert result.total_engines == 81


@pytest.mark.asyncio
async def test_virustotal_rate_limited():
    """Handles HTTP 429 rate limit gracefully without crashing."""
    provider = VirusTotalProvider(api_key="test_dummy_key")
    mock_response = httpx.Response(429, json={"error": "Rate limit exceeded"}, request=httpx.Request("GET", "https://test"))

    with patch.object(httpx.AsyncClient, "get", return_value=mock_response):
        result = await provider.lookup_url("https://example.com")
        assert result.status == ThreatIntelStatus.RATE_LIMITED
        assert result.malicious_count == 0


@pytest.mark.asyncio
async def test_virustotal_not_found():
    """Handles HTTP 404 (URL not known to VirusTotal)."""
    provider = VirusTotalProvider(api_key="test_dummy_key")
    mock_response = httpx.Response(404, json={}, request=httpx.Request("GET", "https://test"))

    with patch.object(httpx.AsyncClient, "get", return_value=mock_response):
        result = await provider.lookup_url("https://fresh-domain.com")
        assert result.status == ThreatIntelStatus.UNKNOWN
        assert result.malicious_count == 0


@pytest.mark.asyncio
async def test_cache_miss_and_hit():
    """Verifies in-memory/mock cache operations for threat intelligence."""
    store = {}

    class MockRedis:
        async def get(self, key):
            return store.get(key)

        async def set(self, key, value, ex=None):
            store[key] = value
            return True

        async def ping(self):
            return True

    cache = ThreatIntelCache(client=MockRedis())
    url_hash = "a" * 64

    # Initial get: cache miss
    res1 = await cache.get(url_hash)
    assert res1 is None

    # Set item
    item = ThreatIntelResult(
        provider_name="VirusTotal v3",
        status=ThreatIntelStatus.CLEAN,
        malicious_count=0,
        suspicious_count=0,
        harmless_count=70,
        total_engines=70,
        categories=[],
        raw_summary="Clean destination",
    )
    await cache.set(url_hash, item)

    # Subsequent get: cache hit
    res2 = await cache.get(url_hash)
    assert res2 is not None
    assert res2.cached is True
    assert res2.status == ThreatIntelStatus.CLEAN
    assert res2.total_engines == 70
