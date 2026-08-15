from fastapi import APIRouter

from app.api.v1.endpoints import access_requests, preview

api_router = APIRouter()
api_router.include_router(preview.router, prefix="/preview", tags=["preview"])
api_router.include_router(access_requests.router, prefix="/access-requests", tags=["access-requests"])
