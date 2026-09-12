from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.schemas.health import RootResponse
from app.database.session import check_db_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    yield
    # Shutdown sequence


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="XEROX Autonomous Cybersecurity Analysis Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/api/health")
async def health_alias():
    db_res = await check_db_health()
    db_status = db_res.get("status", "unknown")
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "XEROX Cybersecurity Core",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }


@app.get("/", response_model=RootResponse)
async def root():
    return RootResponse(
        brand="XEROX",
        product="Autonomous AI Cybersecurity Analysis Platform",
        status="OPERATIONAL",
        version=settings.VERSION,
        docs_url="/docs",
    )
