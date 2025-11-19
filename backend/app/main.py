from fastapi import FastAPI
from app.api.endpoints import health, auth, gardens, trees, analysis, analytics
import uvicorn

app = FastAPI(
    title="Smart Garden API",
    description="API для автоматического учета урожая в садах с использованием ИИ",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(gardens.router, prefix="/api/v1/gardens", tags=["gardens"])
app.include_router(trees.router, prefix="/api/v1/trees", tags=["trees"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Smart Garden API!"}

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )