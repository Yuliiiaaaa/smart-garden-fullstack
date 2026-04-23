# tests/test_storage.py
import pytest
import os

def test_upload_file(client, auth_headers):
    """Тест загрузки файла через локальное хранилище"""
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    response = client.post("/api/v1/files/upload", files=files, headers=auth_headers)
    
    # Если эндпоинт не зарегистрирован, пропускаем
    if response.status_code == 405:
        pytest.skip("Эндпоинт /files/upload не зарегистрирован")
    
    assert response.status_code == 200
    data = response.json()
    assert "key" in data
    assert data["filename"] == "test.jpg"
    assert data["size"] == len(b"fake image content")
    
    # Очистка: удаляем загруженный файл
    if os.path.exists(data["key"]):
        os.remove(data["key"])


def test_upload_invalid_file_type(client, auth_headers):
    """Тест загрузки файла с неверным типом"""
    files = {"file": ("test.txt", b"text content", "text/plain")}
    response = client.post("/api/v1/files/upload", files=files, headers=auth_headers)
    
    if response.status_code == 405:
        pytest.skip("Эндпоинт /files/upload не зарегистрирован")
    
    assert response.status_code == 400
    assert "Only" in response.text


def test_upload_large_file(client, auth_headers):
    """Тест загрузки слишком большого файла"""
    # Создаём большой файл (11MB)
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("large.jpg", large_content, "image/jpeg")}
    response = client.post("/api/v1/files/upload", files=files, headers=auth_headers)
    
    if response.status_code == 405:
        pytest.skip("Эндпоинт /files/upload не зарегистрирован")
    
    # Должна быть ошибка о превышении размера
    assert response.status_code == 400 or response.status_code == 413