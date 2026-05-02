# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Garden API"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./smart_garden.db"

    # S3 / MinIO
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "smart-garden"
    S3_REGION: str = "us-east-1"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_MIME_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]

    # OpenWeatherMap
    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    WEATHER_CACHE_TTL: int = 3600

    class Config:
        env_file = ".env"  # ← эта строка загружает переменные из .env
        env_file_encoding = "utf-8"


settings = Settings()
