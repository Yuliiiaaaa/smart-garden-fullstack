# app/core/token_service.py
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.schemas import TokenData
from app.models.database import User
from app.repositories.token_repository import TokenRepository

class TokenService:
    """
    Сервис для работы с access и refresh токенами.
    Реализует логику аутентификации.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.token_repo = TokenRepository(db)
    
    def create_access_token(self, data: dict) -> str:
        """Создаёт access token (короткоживущий JWT)"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def create_refresh_token(self, user_id: int, user_agent: str = None, 
                             ip: str = None) -> str:
        """Создаёт refresh token (хранится в БД)"""
        token_obj = self.token_repo.create(user_id, user_agent, ip)
        return token_obj.token
    
    def verify_access_token(self, token: str) -> Optional[TokenData]:
        """Проверяет access token и возвращает данные пользователя"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, 
                                 algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            role: str = payload.get("role", "user")
            token_type: str = payload.get("type", "")
            
            if email is None or token_type != "access":
                return None
            return TokenData(email=email, role=role)
        except JWTError:
            return None
    
    def refresh_access_token(self, refresh_token: str, user_agent: str = None, 
                             ip: str = None) -> Optional[Tuple[str, str, User]]:
        """
        Обновляет пару токенов по refresh token.
        Возвращает (new_access_token, new_refresh_token, user) или None.
        Реализует ротацию refresh token (одноразовое использование).
        """
        # 1. Проверяем валидность refresh token
        token_obj = self.token_repo.get_valid_token(refresh_token)
        if not token_obj:
            return None
        
        # 2. Получаем пользователя
        user = self.db.query(User).filter(
            User.id == token_obj.user_id, 
            User.is_active == True
        ).first()
        if not user:
            return None
        
        # 3. Отзываем старый refresh token (ротация)
        self.token_repo.revoke(refresh_token)
        
        # 4. Создаём новую пару
        new_access = self.create_access_token({"sub": user.email, "role": user.role})
        new_refresh = self.create_refresh_token(
            user.id, 
            user_agent or token_obj.user_agent,
            ip or token_obj.ip_address
        )
        
        return new_access, new_refresh, user
    
    def logout(self, refresh_token: str, user_id: int) -> bool:
        """Выход: отзыв конкретного refresh token"""
        return self.token_repo.revoke(refresh_token, user_id)
    
    def logout_all(self, user_id: int) -> int:
        """Выход из всех устройств: отзыв всех refresh token пользователя"""
        return self.token_repo.revoke_all_user_tokens(user_id)