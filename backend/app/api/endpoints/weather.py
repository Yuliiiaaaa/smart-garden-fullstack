from fastapi import APIRouter, Depends, HTTPException
from app.services.weather_service import WeatherService
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/garden/{garden_id}")
async def get_garden_weather(
    garden_id: int,
    lat: float = None,
    lon: float = None,
    weather_service: WeatherService = Depends(),
    current_user = Depends(get_current_user)
):
    
    if not lat or not lon:
        raise HTTPException(400, "Latitude and longitude required")
    data = await weather_service.get_weather(lat, lon)
    return data