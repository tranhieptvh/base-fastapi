from fastapi import APIRouter
from app.api.api_v1.endpoints import ping_router, users_router

api_router = APIRouter()

# Include ping router
api_router.include_router(ping_router, prefix="/ping", tags=["ping"])

# Include users router
api_router.include_router(users_router, prefix="/users", tags=["users"])

# Import and include other routers here
# Example:
# from app.api.api_v1.endpoints import items
# api_router.include_router(items.router, prefix="/items", tags=["items"]) 