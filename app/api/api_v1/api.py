from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, ping, users

api_router = APIRouter()

# Include auth router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include ping router
api_router.include_router(ping.router, prefix="/ping", tags=["ping"])

# Include users router
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Import and include other routers here
# Example:
# from app.api.api_v1.endpoints import items
# api_router.include_router(items.router, prefix="/items", tags=["items"]) 