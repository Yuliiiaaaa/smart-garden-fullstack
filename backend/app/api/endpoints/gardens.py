from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from sqlalchemy import func
from app.models.database import get_db, Garden, User
from app.models.schemas import GardenCreate, GardenUpdate, Garden as GardenSchema
from app.api.dependencies import (
    get_current_user, 
    get_admin_user, 
    get_manager_user,
    get_garden_owner
)

router = APIRouter()

# Публичные эндпоинты (только для чтения)
@router.get("/", response_model=List[GardenSchema])
async def get_gardens(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    # Не требует аутентификации для чтения
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

@router.get("/{garden_id}/stats")
async def get_garden_stats(
    garden_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Доступно всем авторизованным
):
    """Получить статистику по саду"""
    try:
        # Проверяем существование сада
        garden = db.query(Garden).filter(Garden.id == garden_id).first()
        if not garden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сад с ID {garden_id} не найден"
            )
        
        # Получаем статистику по деревьям в саду
        from app.models.database import Tree
        tree_count = db.query(func.count(Tree.id)).filter(Tree.garden_id == garden_id).scalar()
        
        # Получаем последние записи урожая (если есть)
        from app.models.database import HarvestRecord
        harvest_stats = db.query(
            func.count(HarvestRecord.id),
            func.avg(HarvestRecord.fruit_count)
        ).filter(HarvestRecord.tree_id.in_(
            db.query(Tree.id).filter(Tree.garden_id == garden_id)
        )).first()
        
        harvest_count, avg_fruits = harvest_stats if harvest_stats else (0, 0)
        
        return {
            "garden_id": garden_id,
            "garden_name": garden.name,
            "total_trees": tree_count or 0,
            "area_hectares": garden.area,
            "tree_density": round(tree_count / garden.area, 2) if garden.area > 0 else 0,
            "harvest_records_count": harvest_count or 0,
            "average_fruits_per_tree": round(avg_fruits, 2) if avg_fruits else 0,
            "created_at": garden.created_at.isoformat() if garden.created_at else None,
            "fruit_type": garden.fruit_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )

# Защищенные эндпоинты (требуют аутентификации)
@router.post("/", response_model=GardenSchema, status_code=status.HTTP_201_CREATED)
async def create_garden(
    garden: GardenCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Требует аутентификации
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
    current_user: User = Depends(get_manager_user)  # Требует прав менеджера или выше
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
    current_user: User = Depends(get_admin_user)  # Требует прав администратора
):
    """Удалить сад (только для администраторов)"""
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

@router.get("/{garden_id}/stats")
async def get_garden_stats(
    garden_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_manager_user)  # Требует прав менеджера или выше
):
    """Получить статистику по саду (только для менеджеров и администраторов)"""
    try:
        garden = db.query(Garden).filter(Garden.id == garden_id).first()
        if not garden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сад с ID {garden_id} не найден"
            )
        
        # Получаем статистику по деревьям в саду
        from app.models.database import Tree
        tree_count = db.query(func.count(Tree.id)).filter(Tree.garden_id == garden_id).scalar()
        
        return {
            "garden_id": garden_id,
            "garden_name": garden.name,
            "total_trees": tree_count,
            "area": garden.area,
            "tree_density": tree_count / garden.area if garden.area > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )