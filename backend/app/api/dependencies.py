from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.models.database import get_db, User
from app.models.schemas import UserRole

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получает текущего пользователя из токена"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь деактивирован",
        )
    
    return user

# Зависимости для проверки ролей
async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Проверяет что пользователь администратор"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user

async def get_manager_user(current_user: User = Depends(get_current_user)):
    """Проверяет что пользователь менеджер или администратор"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права менеджера или администратора"
        )
    return current_user

async def get_garden_owner(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Проверяет что пользователь является владельцем сада
    или имеет достаточные права
    """
    from app.models.database import Garden
    
    garden = db.query(Garden).filter(Garden.id == garden_id).first()
    if not garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сад с ID {garden_id} не найден"
        )
    
    # В будущем можно добавить связь пользователь-сад
    # Пока разрешаем всем авторизованным пользователям
    if current_user.role not in ["admin", "manager"]:
        # Здесь можно добавить проверку на владение садом
        pass
    
    return current_user