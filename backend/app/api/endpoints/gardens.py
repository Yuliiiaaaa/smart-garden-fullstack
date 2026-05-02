# app/api/endpoints/gardens.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.models.schemas import (
    GardenCreate,
    GardenUpdate,
    Garden as GardenSchema,
    SortOrder,
    GardenFilterParams,
)
from app.models.database import get_db, Garden, User, Tree, HarvestRecord
from app.models.schemas import (
    GardenCreate,
    GardenUpdate,
    Garden as GardenSchema,
    GardenFilterParams,
)
from app.api.dependencies import get_current_user, get_manager_user, get_admin_user
from fastapi.responses import JSONResponse

router = APIRouter()


# Публичный эндпоинт (доступен всем аутентифицированным)
@router.get("/", response_model=List[GardenSchema])
async def get_gardens(
    params: GardenFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):  # теперь доступно только авторизованным

    query = db.query(Garden)

    # Применение фильтров
    if params.name:
        query = query.filter(Garden.name.ilike(f"%{params.name}%"))
    if params.location:
        query = query.filter(Garden.location.ilike(f"%{params.location}%"))
    if params.fruit_type:
        query = query.filter(Garden.fruit_type == params.fruit_type)
    if params.area_min is not None:
        query = query.filter(Garden.area >= params.area_min)
    if params.area_max is not None:
        query = query.filter(Garden.area <= params.area_max)
    if params.search:
        query = query.filter(
            (Garden.name.ilike(f"%{params.search}%"))
            | (Garden.location.ilike(f"%{params.search}%"))
        )

    # Сортировка
    sort_column = getattr(Garden, params.sort_by, Garden.name)
    if params.sort_order == SortOrder.DESC:
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Пагинация
    gardens = query.offset(params.skip).limit(params.limit).all()
    return gardens


@router.get("/{garden_id}/stats", response_model=dict)
async def get_garden_stats(
    garden_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    garden = db.query(Garden).filter(Garden.id == garden_id).first()
    if not garden:
        raise HTTPException(status_code=404, detail="Сад не найден")

    tree_count = (
        db.query(func.count(Tree.id)).filter(Tree.garden_id == garden_id).scalar() or 0
    )
    harvest_stats = (
        db.query(func.count(HarvestRecord.id), func.avg(HarvestRecord.fruit_count))
        .filter(HarvestRecord.garden_id == garden_id)
        .first()
    )
    harvest_count, avg_fruits = harvest_stats or (0, 0)

    return {
        "garden_id": garden_id,
        "garden_name": garden.name,
        "total_trees": tree_count,
        "area_hectares": garden.area,
        "tree_density": round(tree_count / garden.area, 2) if garden.area > 0 else 0,
        "harvest_records_count": harvest_count or 0,
        "average_fruits_per_tree": round(avg_fruits, 2) if avg_fruits else 0,
        "created_at": garden.created_at.isoformat() if garden.created_at else None,
        "fruit_type": garden.fruit_type,
    }


@router.post("/", response_model=GardenSchema, status_code=201)
async def create_garden(
    garden: GardenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_manager_user),  # только менеджер и выше
):
    existing = db.query(Garden).filter(Garden.name == garden.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Сад с таким названием уже существует"
        )
    db_garden = Garden(**garden.dict())
    db.add(db_garden)
    db.commit()
    db.refresh(db_garden)
    return db_garden


@router.put("/{garden_id}", response_model=GardenSchema)
async def update_garden(
    garden_id: int,
    garden_update: GardenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_manager_user),  # только менеджер и выше
):
    db_garden = db.query(Garden).filter(Garden.id == garden_id).first()
    if not db_garden:
        raise HTTPException(status_code=404, detail="Сад не найден")
    update_data = garden_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_garden, field, value)
    db.commit()
    db.refresh(db_garden)
    return db_garden


@router.delete("/{garden_id}")
async def delete_garden(
    garden_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),  # только администратор
):
    db_garden = db.query(Garden).filter(Garden.id == garden_id).first()
    if not db_garden:
        raise HTTPException(status_code=404, detail="Сад не найден")
    db.delete(db_garden)
    db.commit()
    return {"message": f"Сад '{db_garden.name}' удалён", "deleted_id": garden_id}


@router.get("/{garden_id}/jsonld", include_in_schema=False)
async def garden_jsonld(garden_id: int, db: Session = Depends(get_db)):
    """Структурированные данные JSON-LD для поисковых систем"""
    garden = db.query(Garden).filter(Garden.id == garden_id).first()
    if not garden:
        raise HTTPException(status_code=404, detail="Сад не найден")

    json_ld = {
        "@context": "https://schema.org",
        "@type": "Place",
        "name": garden.name,
        "description": garden.description
        or f"Сад {garden.name} площадью {garden.area} га, выращивание {garden.fruit_type}.",
        "address": {"@type": "PostalAddress", "addressLocality": garden.location},
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": 0,  # можно добавить реальные координаты
            "longitude": 0,
        },
        "hasMap": f"https://smart-garden.ru/gardens/{garden_id}",
        "url": f"https://smart-garden.ru/gardens/{garden_id}",
    }

    return JSONResponse(content=json_ld, media_type="application/ld+json")
