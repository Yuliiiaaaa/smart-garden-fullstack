# app/services/weather_service.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi import HTTPException
from app.core.config import settings
from app.core.cache import cache


class WeatherService:
    def __init__(self):
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.api_key = settings.OPENWEATHER_API_KEY
        self.client = httpx.AsyncClient(timeout=10.0)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_weather(self, lat: float, lon: float) -> dict:
        # Если нет API ключа, возвращаем тестовые данные
        if not self.api_key or self.api_key == "your_api_key_here":
            return {
                "temperature": 18.5,
                "feels_like": 17.2,
                "humidity": 65,
                "description": "облачно с прояснениями",
                "icon": "04d",
                "wind_speed": 3.2
            }

        cache_key = f"weather_{lat}_{lon}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "lang": "ru"
        }
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            normalized = {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "wind_speed": data["wind"]["speed"]
            }
            cache.set(cache_key, normalized, ttl=settings.WEATHER_CACHE_TTL)
            return normalized
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Weather API error")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Weather service unavailable: {str(e)}")

    async def close(self):
        await self.client.aclose()