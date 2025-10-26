from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

# Временные модели (заглушки)
class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login")
async def login(user_data: UserLogin):
    """Эндпоинт для входа пользователя"""
    # Заглушка - в реальности здесь будет проверка в БД
    if user_data.email == "demo@smartgarden.com" and user_data.password == "demo":
        return Token(
            access_token="demo_token_12345",
            token_type="bearer"
        )
    raise HTTPException(status_code=401, detail="Неверные учетные данные")

@router.post("/register")
async def register(user_data: UserLogin):
    """Эндпоинт для регистрации нового пользователя"""
    # Заглушка
    return {
        "message": "Пользователь успешно зарегистрирован",
        "user_id": 1,
        "email": user_data.email
    }