from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class AnalyticsData(BaseModel):
    period: str
    total_fruits: int
    growth_percentage: float
    top_trees: List[Dict]

@router.get("/overview")
async def get_analytics_overview(garden_id: int = None, period: str = "month"):
    """Получить общую аналитику"""
    return AnalyticsData(
        period="Сентябрь 2024",
        total_fruits=1850,
        growth_percentage=18.5,
        top_trees=[
            {"tree_id": 45, "fruit_count": 65},
            {"tree_id": 12, "fruit_count": 58},
            {"tree_id": 78, "fruit_count": 52}
        ]
    )

@router.get("/growth")
async def get_growth_analytics(garden_id: int = None):
    """Получить данные по росту урожайности"""
    return {
        "weekly_data": [
            {"week": "Неделя 1", "fruits": 350},
            {"week": "Неделя 2", "fruits": 415},
            {"week": "Неделя 3", "fruits": 485},
            {"week": "Неделя 4", "fruits": 600}
        ],
        "growth_trend": "positive"
    }

@router.get("/predictions")
async def get_predictions(garden_id: int = None):
    """Получить прогнозы урожайности"""
    return {
        "predicted_harvest": 2450,
        "confidence": 0.87,
        "recommended_harvest_date": "2024-10-05",
        "risk_factors": ["погодные условия", "вредители"]
    }