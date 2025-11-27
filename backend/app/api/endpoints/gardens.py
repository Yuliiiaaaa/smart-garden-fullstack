from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, Garden, User
from app.models.schemas import GardenCreate, GardenUpdate, Garden as GardenSchema
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[GardenSchema])
async def get_gardens(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Добавляем аутентификацию
):
    """Получить список всех садов с пагинацией"""
    try:
        gardens = db.query(Garden).offset(skip).limit(limit).all()
        return gardens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка садов: {str(e)}"
        )

@router.get("/{garden_id}", response_model=GardenSchema)
async def get_garden(
    garden_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Добавляем аутентификацию
):
    """Получить информацию о конкретном саде по ID"""
    garden = db.query(Garden).filter(Garden.id == garden_id).first()
    if not garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сад с ID {garden_id} не найден"
        )
    return garden

@router.post("/", response_model=GardenSchema, status_code=status.HTTP_201_CREATED)
async def create_garden(
    garden: GardenCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Добавляем аутентификацию
):
    """Создать новый сад"""
    try:
        # Проверяем, нет ли сада с таким же названием
        existing_garden = db.query(Garden).filter(Garden.name == garden.name).first()
        if existing_garden:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сад с таким названием уже существует"
            )
        
        # Создаем новый сад
        db_garden = Garden(**garden.dict())
        db.add(db_garden)
        db.commit()
        db.refresh(db_garden)
        
        return db_garden
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании сада: {str(e)}"
        )

@router.put("/{garden_id}", response_model=GardenSchema)
async def update_garden(
    garden_id: int, 
    garden_update: GardenUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Добавляем аутентификацию
):
    """Обновить информацию о саде"""
    try:
        db_garden = db.query(Garden).filter(Garden.id == garden_id).first()
        if not db_garden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сад с ID {garden_id} не найден"
            )
        
        # Обновляем только переданные поля
        update_data = garden_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_garden, field, value)
        
        db.commit()
        db.refresh(db_garden)
        
        return db_garden
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении сада: {str(e)}"
        )

@router.delete("/{garden_id}")
async def delete_garden(
    garden_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Добавляем аутентификацию
):
    """Удалить сад"""
    try:
        db_garden = db.query(Garden).filter(Garden.id == garden_id).first()
        if not db_garden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сад с ID {garden_id} не найден"
            )
        
        db.delete(db_garden)
        db.commit()
        
        return {
            "message": f"Сад '{db_garden.name}' успешно удален",
            "deleted_id": garden_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении сада: {str(e)}"
        )