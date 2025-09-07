from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App settings
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/ai_creat"
    
    # Redis/Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/x-photoshop"]
    
    # AI Providers
    AI_PROVIDER: str = "gemini"  # openai, gemini
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    USE_GEMINI_IMAGE_EDITOR: bool = True
    GEMINI_IMAGE_EDITOR_MODEL: str = "gemini-2.5-flash-image-preview"
    GEMINI_ANALYSIS_MODEL: str = "gemini-2.5-pro"
    GEMINI_TEXT_MODEL: str = "gemini-2.5-flash"

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3002", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"


settings = Settings()
