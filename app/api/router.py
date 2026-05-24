from fastapi import APIRouter

from app.features.auth.router import router as auth_router
from app.features.operational.router import router as operational_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(operational_router)
