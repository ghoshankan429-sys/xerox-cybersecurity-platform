from fastapi import APIRouter
from app.api.v1 import auth, health, analyze

api_router = APIRouter()

# Register v1 routes
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(auth.router, prefix="", tags=["Authentication"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
api_router.include_router(analyze.router, prefix="/scans", tags=["Scans"])
