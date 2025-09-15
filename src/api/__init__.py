from fastapi import APIRouter
from src.core.config import settings

# Create main router
api_router = APIRouter()

# Import all routers
from src.api.ping import router as ping_router
from src.api.users import router as users_router
from src.api.auth import router as auth_router
from src.api.vocabulary import router as vocabulary_router

# Include all routers with their prefixes
api_router.include_router(ping_router, prefix="/ping", tags=["ping"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(vocabulary_router, prefix="/vocabulary", tags=["vocabulary"])

__all__ = ["api_router"]
