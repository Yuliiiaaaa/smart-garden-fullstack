# app/repositories/token_repository.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app.models.database import RefreshToken
from app.core.config import settings


class TokenRepository:
    """
    Репозиторий для работы с refresh токенами в БД.
    Инкапсулирует все запросы к таблице refresh_tokens.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> RefreshToken:
        """Создаёт новый refresh token в БД"""
        token_str = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        db_token = RefreshToken(
            token=token_str,
            user_id=user_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            revoked=False,
        )
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """Получает валидный (не отозванный, не истекший) токен"""
        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token == token,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
            .first()
        )

    def revoke(self, token: str, user_id: Optional[int] = None) -> bool:
        """Отзывает конкретный токен"""
        query = self.db.query(RefreshToken).filter(RefreshToken.token == token)
        if user_id:
            query = query.filter(RefreshToken.user_id == user_id)
        token_obj = query.first()
        if token_obj:
            token_obj.revoked = True
            self.db.commit()
            return True
        return False

    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Отзывает все токены пользователя"""
        result = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .update({"revoked": True})
        )
        self.db.commit()
        return result

    def cleanup_expired(self) -> int:
        """Удаляет истекшие токены (для очистки)"""
        result = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.expires_at <= datetime.utcnow())
            .delete()
        )
        self.db.commit()
        return result
