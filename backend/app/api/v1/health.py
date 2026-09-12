from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="XEROX Autonomous Cybersecurity Engine",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database="ready",
        cache="ready",
    )
