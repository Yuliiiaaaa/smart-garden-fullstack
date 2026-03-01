# app/api/endpoints/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.models.database import get_db, User
from app.models.schemas import UserCreate, User as UserSchema, Token, UserLogin
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.api.dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.options("/login")
async def login_options():
    """OPTIONS handler for login endpoint"""
    return {"message": "OK"}

@router.options("/register")
async def register_options():
    """OPTIONS handler for register endpoint"""
    return {"message": "OK"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Аутентификация пользователя"""
    print(f"Login attempt for email: {user_data.email}")
    
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        print(f"Login failed for {user_data.email}: invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        print(f"Login failed for {user_data.email}: user inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь деактивирован",
        )
    
    # Создаем токен с role в payload
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    print(f"Login successful for {user_data.email} with role {user.role}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    print(f"Register attempt for email: {user_data.email}")
    
    try:
        # Проверяем, нет ли пользователя с таким email
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            print(f"Register failed for {user_data.email}: email already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем нового пользователя
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role if hasattr(user_data, 'role') else "user"
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"Register successful for {user_data.email} with role {db_user.role}")
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Register error for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации: {str(e)}"
        )

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user

@router.get("/users", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Получить список всех пользователей (только для администратора)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Получить информацию о конкретном пользователе (только для администратора)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.put("/users/{user_id}/role", response_model=UserSchema)
async def change_user_role(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Изменить роль пользователя (доступно только администратору)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    new_role = role_data.get("role")
    if new_role not in ["admin", "manager", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимая роль. Допустимые значения: admin, manager, user"
        )

    # Не даем админу понизить самого себя
    if user.id == current_user.id and new_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить собственную роль"
        )

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user