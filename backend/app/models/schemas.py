from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import EmailStr
from typing import Optional

class FruitType(str, Enum):
    APPLE = "apple"
    PEAR = "pear"
    CHERRY = "cherry"
    PLUM = "plum"

# Схемы для Garden
class GardenBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название сада")
    location: str = Field(..., min_length=1, max_length=200, description="Местоположение")
    area: float = Field(..., gt=0, description="Площадь в гектарах")
    fruit_type: FruitType = Field(..., description="Тип плодов")
    description: Optional[str] = Field(None, max_length=500, description="Описание")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Название сада не может быть пустым')
        return v.strip()

    @validator('area')
    def area_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Площадь должна быть положительным числом')
        return v

class GardenCreate(GardenBase):
    pass

class GardenUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    area: Optional[float] = Field(None, gt=0)
    fruit_type: Optional[FruitType] = None
    description: Optional[str] = Field(None, max_length=500)

class Garden(GardenBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для Tree
class TreeBase(BaseModel):
    garden_id: int = Field(..., gt=0, description="ID сада")
    row_number: int = Field(..., gt=0, description="Номер ряда")
    tree_number: int = Field(..., gt=0, description="Номер дерева")
    variety: str = Field(..., min_length=1, max_length=50, description="Сорт")
    planting_year: Optional[int] = Field(None, ge=1900, le=2100, description="Год посадки")

class TreeCreate(TreeBase):
    pass

class Tree(TreeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для аутентификации
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Пароль должен быть не менее 6 символов")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None