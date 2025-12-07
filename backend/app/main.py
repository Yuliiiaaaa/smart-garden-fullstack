from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from app.api.endpoints import health, auth, gardens, trees, analysis, analytics
import uvicorn

# Создаем OAuth2 схему для Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

app = FastAPI(
    title="Smart Garden API",
    description="API для автоматического учета урожая в садах с использованием ИИ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # Добавляем настройки авторизации для Swagger
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints"
        },
        {
            "name": "authentication",
            "description": "Authentication endpoints"
        },
        {
            "name": "gardens",
            "description": "Operations with gardens"
        },
        {
            "name": "trees",
            "description": "Operations with trees"
        },
        {
            "name": "analysis",
            "description": "Photo analysis endpoints"
        },
        {
            "name": "analytics",
            "description": "Analytics endpoints"
        }
    ]
)

# Подключаем роутеры
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(gardens.router, prefix="/api/v1/gardens", tags=["gardens"])
app.include_router(trees.router, prefix="/api/v1/trees", tags=["trees"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Smart Garden API!"}

@app.get("/api/status")
async def api_status(token: str = Depends(oauth2_scheme)):
    """Проверка статуса API с аутентификацией"""
    return {"status": "API is running", "authenticated": True}

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True
    )