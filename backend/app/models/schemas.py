# app/models/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import EmailStr

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
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = Field(default=UserRole.USER, description="Роль пользователя")

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
    role: Optional[str] = None

# Схемы для анализа изображений
class DetectedFruit(BaseModel):
    fruit_type: str = Field(..., description="Тип фрукта")
    count: int = Field(..., ge=0, description="Количество")
    confidence: float = Field(..., ge=0, le=1, description="Уверенность (0-1)")
    boxes: List[Dict[str, Any]] = Field(default_factory=list, description="Bounding boxes")

class AnalysisResult(BaseModel):
    fruit_count: int = Field(..., ge=0, description="Количество обнаруженных плодов")
    confidence: float = Field(..., ge=0, le=1, description="Уверенность модели (0-1)")
    processing_time: float = Field(..., gt=0, description="Время обработки в секундах")
    detected_fruits: List[DetectedFruit] = Field(default_factory=list, description="Список обнаруженных фруктов")
    recommendations: str = Field(..., description="Рекомендации на основе анализа")
    record_id: Optional[int] = Field(None, description="ID записи в базе данных")
    method: str = Field(..., description="Метод анализа")
    model: Optional[str] = Field(None, description="Используемая модель ИИ")
    image_url: Optional[str] = Field(None, description="URL изображения")
    
    class Config:
        from_attributes = True

# Схема для загрузки файла
class ImageUpload(BaseModel):
    tree_id: Optional[int] = Field(None, description="ID дерева")
    fruit_type: str = Field("apple", description="Ожидаемый тип плодов")
    garden_id: Optional[int] = Field(None, description="ID сада")

# Схема для истории анализов
class HarvestRecordResponse(BaseModel):
    id: int
    tree_id: Optional[int]
    garden_id: Optional[int]
    garden_name: Optional[str]
    fruit_type: Optional[str]
    harvest_date: Optional[str]
    fruit_count: int
    confidence: Optional[float]
    processing_time: Optional[float]
    image_url: Optional[str]
    created_at: Optional[str]

class AnalysisHistoryResponse(BaseModel):
    analyses: List[HarvestRecordResponse]
    total: int
    user: Dict[str, Any]