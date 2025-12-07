from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.security import verify_token
import time

async def auth_middleware(request: Request, call_next):
    """
    Middleware для проверки аутентификации и авторизации
    
    Пропускает публичные эндпоинты:
    - /, /docs, /redoc, /openapi.json
    - /api/v1/health
    - /api/v1/auth/login, /api/v1/auth/register
    """
    
    # Публичные эндпоинты (полные пути)
    public_paths = [
        "/",
        "/docs", 
        "/redoc", 
        "/openapi.json",
        "/api/v1/health", 
        "/api/v1/health/detailed",
        "/api/v1/auth/login", 
        "/api/v1/auth/register"
    ]
    
    # Проверяем если текущий путь публичный
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Для остальных путей проверяем JWT токен
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Требуется авторизация. Используйте Bearer token."}
        )
    
    token = auth_header.split(" ")[1]
    
    # Проверяем токен
    token_data = verify_token(token)
    if not token_data:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Неверный или просроченный токен"}
        )
    
    # Добавляем информацию о пользователе в request state
    request.state.user_email = token_data.email
    request.state.user_role = token_data.role
    
    # Логирование запроса
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path} - User: {token_data.email} ({token_data.role})")
    
    return await call_next(request)

async def role_middleware(request: Request, call_next):
    """
    Middleware для проверки ролей пользователей
    
    Доступ к эндпоинтам:
    - DELETE /gardens/{id} - только для admin
    - GET /gardens/stats - только для admin и manager
    - PUT /gardens/{id} - admin, manager, owner
    """
    
    # Проверяем защищенные пути
    path = request.url.path
    
    # Если это не защищенный путь, пропускаем
    if not ("/gardens/" in path or "/trees/" in path):
        return await call_next(request)
    
    # Получаем email пользователя из request state
    user_email = getattr(request.state, 'user_email', None)
    if not user_email:
        return await call_next(request)
    
    # Здесь в реальном приложении мы бы доставали роль из БД
    # Для упрощения будем проверять в зависимостях
    
    return await call_next(request)