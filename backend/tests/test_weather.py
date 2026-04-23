# tests/test_weather.py
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from app.services.weather_service import WeatherService


@pytest.mark.asyncio
async def test_weather_service_mocked():
    """Тест погодного сервиса с моком - упрощённая версия"""
    service = WeatherService()
    
    # Сохраняем оригинальный ключ
    from app.core.config import settings
    original_key = settings.OPENWEATHER_API_KEY
    settings.OPENWEATHER_API_KEY = "test_key"
    
    mock_response = {
        "main": {"temp": 20.5, "feels_like": 19.0, "humidity": 60},
        "weather": [{"description": "clear sky", "icon": "01d"}],
        "wind": {"speed": 2.5}
    }
    
    # Мокаем весь метод client.get через patch
    async def mock_get(*args, **kwargs):
        class MockResponse:
            async def raise_for_status(self):
                pass
            def json(self):
                return mock_response
        return MockResponse()
    
    with patch.object(service.client, 'get', side_effect=mock_get):
        result = await service.get_weather(55.75, 37.62)
        assert result["temperature"] == 20.5
        assert result["humidity"] == 60
    
    settings.OPENWEATHER_API_KEY = original_key


@pytest.mark.asyncio
async def test_weather_service_fallback_no_key():
    """Тест возврата fallback данных при отсутствии API ключа"""
    from app.core.config import settings
    original_key = settings.OPENWEATHER_API_KEY
    settings.OPENWEATHER_API_KEY = ""
    
    service = WeatherService()
    result = await service.get_weather(55.75, 37.62)
    
    # Должны вернуться fallback данные
    assert "temperature" in result
    assert result["temperature"] == 18.5
    assert "humidity" in result
    
    settings.OPENWEATHER_API_KEY = original_key


def test_get_weather_success(client, auth_headers, mocker):
    """Тест эндпоинта погоды"""
    # Мокаем сервис
    mock_weather = {
        "temperature": 18.5,
        "feels_like": 17.2,
        "humidity": 65,
        "description": "облачно",
        "icon": "04d",
        "wind_speed": 3.2
    }
    mocker.patch("app.services.weather_service.WeatherService.get_weather", 
                 return_value=mock_weather)
    
    response = client.get("/api/v1/weather/garden/1?lat=55.75&lon=37.62", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == 18.5
    assert data["humidity"] == 65


def test_weather_fallback_on_error(client, auth_headers, mocker):
    """Тест обработки ошибки погодного сервиса"""
    # Мокаем ошибку
    mocker.patch("app.services.weather_service.WeatherService.get_weather",
                 side_effect=HTTPException(status_code=503, detail="Weather service unavailable"))
    
    response = client.get("/api/v1/weather/garden/1?lat=55.75&lon=37.62", headers=auth_headers)
    assert response.status_code == 503
    assert "unavailable" in response.text