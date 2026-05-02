# app/api/endpoints/auth.py
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, User
from app.models.schemas import (
    UserCreate,
    User as UserSchema,
    UserLogin,
    Token,
    RefreshTokenRequest,
    LogoutRequest,
)
from app.core.security import get_password_hash, verify_password
from app.core.token_service import TokenService
from app.api.dependencies import get_current_user, get_admin_user

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Вход в систему, получение пары токенов"""
    # Поиск пользователя
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь деактивирован"
        )

    # Создание токенов через сервис
    token_service = TokenService(db)
    access_token = token_service.create_access_token(
        {"sub": user.email, "role": user.role}
    )
    refresh_token = token_service.create_refresh_token(
        user_id=user.id,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)
):
    """Обновление access token по refresh token"""
    token_service = TokenService(db)
    result = token_service.refresh_access_token(
        refresh_token=token_data.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный refresh token",
        )

    new_access, new_refresh, user = result
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Выход: отзыв refresh token"""
    token_service = TokenService(db)
    token_service.logout(logout_data.refresh_token, current_user.id)
    return {"message": "Выход выполнен успешно"}


@router.post("/logout-all")
async def logout_all(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Выход со всех устройств"""
    token_service = TokenService(db)
    count = token_service.logout_all(current_user.id)
    return {"message": f"Завершено {count} сессий"}


@router.post("/register", response_model=UserSchema, status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    hashed = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        role="user",  # По умолчанию обычный пользователь
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Информация о текущем пользователе"""
    return current_user


# Административные эндпоинты (из лабораторной №1)
@router.get("/users", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Список всех пользователей (только admin)"""
    return db.query(User).offset(skip).limit(limit).all()


@router.put("/users/{user_id}/role", response_model=UserSchema)
async def change_user_role(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Изменение роли пользователя (только admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_role = role_data.get("role")
    if new_role not in ["admin", "manager", "user"]:
        raise HTTPException(status_code=400, detail="Недопустимая роль")

    # Не даем админу понизить самого себя
    if user.id == current_user.id and new_role != "admin":
        raise HTTPException(status_code=400, detail="Нельзя изменить собственную роль")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user
