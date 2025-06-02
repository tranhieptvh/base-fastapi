from fastapi import FastAPI
from src.core.config import settings
from src.api import api_router
from src.core.middleware import setup_middleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json"
)

# Setup all middleware
setup_middleware(app)

app.include_router(api_router, prefix=settings.API_STR)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"} 