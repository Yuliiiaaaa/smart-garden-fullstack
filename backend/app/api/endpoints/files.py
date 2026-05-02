# app/api/endpoints/files.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.dependencies import get_current_user
from app.models.database import User
import uuid
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), current_user: User = Depends(get_current_user)
):
    """Загрузка файла"""
    # Проверка типа файла
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Only {', '.join(allowed_types)} images allowed")

    # Проверка размера файла (читаем первые байты, чтобы не загружать весь файл)
    first_chunk = await file.read(MAX_FILE_SIZE + 1)
    if len(first_chunk) > MAX_FILE_SIZE:
        raise HTTPException(
            413, f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)} MB"
        )

    # Получаем расширение файла
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Сохраняем файл (нужно дочитать остаток, если есть)
    # Но мы уже прочитали первый чанк, который может быть всем файлом
    if len(first_chunk) > 0:
        with open(filepath, "wb") as f:
            f.write(first_chunk)
            # Читаем и записываем остаток, если файл больше
            while chunk := await file.read(8192):
                f.write(chunk)

    return {
        "key": filepath,
        "filename": file.filename,
        "size": os.path.getsize(filepath),
    }
