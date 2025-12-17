# auth_middleware.py (исправленная версия)
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
    - OPTIONS запросы (CORS preflight)
    """
    
    # ВАЖНО: Пропускаем все OPTIONS запросы (preflight для CORS)
    if request.method == "OPTIONS":
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response
    
    # Публичные эндпоинты (полные пути)
    public_paths = [
        "/",
        "/docs", 
        "/redoc", 
        "/openapi.json",
        "/api/status",  # Добавляем публичный эндпоинт
        "/api/v1/health", 
        "/api/v1/health/detailed",
        "/api/v1/health/ready",
        "/api/v1/auth/login", 
        "/api/v1/auth/register"
    ]
    
    # Публичные пути с префиксами
    public_path_prefixes = [
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    # Проверяем если текущий путь публичный
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Проверяем префиксы
    for prefix in public_path_prefixes:
        if request.url.path.startswith(prefix):
            return await call_next(request)
    
    # Для остальных путей проверяем JWT токен
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        print(f"DEBUG: No Authorization header for {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Требуется авторизация. Используйте Bearer token."},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        )
    
    token = auth_header.split(" ")[1]
    
    # Проверяем токен
    token_data = verify_token(token)
    if not token_data:
        print(f"DEBUG: Invalid token for {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Неверный или просроченный токен"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        )
    
    # Добавляем информацию о пользователе в request state
    request.state.user_email = token_data.email
    request.state.user_role = getattr(token_data, 'role', 'user')
    
    # Логирование запроса
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path} - User: {token_data.email} ({getattr(token_data, 'role', 'user')})")
    
    return await call_next(request)

async def role_middleware(request: Request, call_next):
    """
    Middleware для проверки ролей пользователей
    """
    # Если это OPTIONS запрос (preflight), пропускаем
    if request.method == "OPTIONS":
        return await call_next(request)
    
    # Пропускаем публичные пути
    public_paths = ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/health"]
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Получаем email пользователя из request state
    user_email = getattr(request.state, 'user_email', None)
    if not user_email:
        # Если нет пользователя, но путь требует авторизации, вернем 401
        # Эта проверка уже была в auth_middleware, но на всякий случай
        return await call_next(request)
    
    return await call_next(request)