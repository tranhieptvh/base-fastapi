from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, ConfigDict

class Settings(BaseSettings):
    # API
    API_STR: str = "/api"
    PROJECT_NAME: str = "FastAPI Project"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]
    
    # Frontend URL for email templates
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    MYSQL_ROOT_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_MAX_TASKS_PER_CHILD: int = 1000
    CELERY_MAX_MEMORY_PER_CHILD: int = 200000

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return self.DATABASE_URL

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 