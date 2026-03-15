# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Garden API"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 минут
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7      # 7 дней
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "smart-garden"
    S3_REGION: str = "us-east-1"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_MIME_TYPES: list = ["image/jpeg", "image/png", "image/jpg"]
    # Database
    DATABASE_URL: str = "sqlite:///./smart_garden.db"
    

    class Config:
        env_file = ".env"

settings = Settings()