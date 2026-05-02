# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.api.endpoints import (
    health,
    auth,
    gardens,
    trees,
    analysis,
    analytics,
    seo,
    weather,
    files,
)
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Создаем security схему для Swagger
security_scheme = HTTPBearer(
    scheme_name="JWT",
    bearerFormat="JWT",
    description="Введите токен в формате: Bearer <ваш_токен>",
)

app = FastAPI(
    title="Smart Garden API",
    description="API для автоматического учета урожая в садах с использованием ИИ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "authentication", "description": "Authentication endpoints"},
        {"name": "gardens", "description": "Operations with gardens"},
        {"name": "trees", "description": "Operations with trees"},
        {"name": "analysis", "description": "Photo analysis endpoints"},
        {"name": "analytics", "description": "Analytics endpoints"},
    ],
    openapi_extra={
        "components": {
            "securitySchemes": {
                "JWT": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Введите JWT токен в формате: Bearer <token>",
                }
            }
        },
        "security": [{"JWT": []}],
    },
)

# 1. ВАЖНО: CORS middleware ДОЛЖЕН быть ПЕРВЫМ
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 2. Затем кастомные middleware
from app.middleware.auth_middleware import auth_middleware, role_middleware

app.middleware("http")(auth_middleware)
app.middleware("http")(role_middleware)

# Подключаем роутеры
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(gardens.router, prefix="/api/v1/gardens", tags=["gardens"])
app.include_router(trees.router, prefix="/api/v1/trees", tags=["trees"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(seo.router, tags=["seo"])


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Smart Garden API!"}


@app.get("/api/status")
async def api_status():
    """Публичный эндпоинт для проверки статуса API"""
    return {"status": "API is running", "authenticated": False}


# Обработчик OPTIONS для всех путей
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Обработчик OPTIONS запросов для всех путей"""
    return {"message": "OK"}


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Страница не найдена"})


# Запуск сервера
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
