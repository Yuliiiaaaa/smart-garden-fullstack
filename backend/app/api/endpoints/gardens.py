from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Garden(BaseModel):
    id: int
    name: str
    location: str
    tree_count: int

# Временные данные
demo_gardens = [
    {"id": 1, "name": "Яблоневый сад", "location": "Московская область", "tree_count": 150},
    {"id": 2, "name": "Грушевый сад", "location": "Калужская область", "tree_count": 80}
]

@router.get("/")
async def get_gardens():
    """Получить список всех садов"""
    return demo_gardens

@router.get("/{garden_id}")
async def get_garden(garden_id: int):
    """Получить информацию о конкретном саде"""
    garden = next((g for g in demo_gardens if g["id"] == garden_id), None)
    if not garden:
        raise HTTPException(status_code=404, detail="Сад не найден")
    return garden