from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Smart Garden API",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    process = psutil.Process(os.getpid())
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "process": {
            "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent()
        },
        "api": {
            "active_endpoints": 6,
            "database_connected": True  # В будущем заменить на реальную проверку
        }
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes/docker"""
    # Здесь можно добавить проверки подключения к БД, внешним сервисам и т.д.
    checks = {
        "database": True,  # Заглушка
        "ai_service": True,  # Заглушка
        "file_storage": True  # Заглушка
    }
    
    is_ready = all(checks.values())
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }