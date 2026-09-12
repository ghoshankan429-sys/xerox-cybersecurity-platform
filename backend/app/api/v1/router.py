from fastapi import APIRouter
from app.api.v1 import auth, health

api_router = APIRouter()

# Register v1 routes
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(auth.router, prefix="", tags=["Authentication"])
