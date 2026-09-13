from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.schemas.health import HealthResponse
from app.database.session import check_db_health
from app.cache.redis_client import check_redis_health

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    db_result = await check_db_health()
    db_status = db_result.get("status", "unknown")

    cache_result = await check_redis_health()
    cache_status = cache_result.get("status", "unknown")

    is_healthy = db_status == "connected"
    overall_status = "healthy" if is_healthy else "degraded"

    payload = HealthResponse(
        status=overall_status,
        service="XEROX Autonomous Cybersecurity Engine",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        cache=cache_status,
    )

    if not is_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload.model_dump(),
        )

    return payload
