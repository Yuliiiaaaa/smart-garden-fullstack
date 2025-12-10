import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

def save_uploaded_file(upload_file, upload_dir: str = "uploads") -> Optional[str]:
    """Сохраняет загруженный файл и возвращает путь"""
    try:
        # Создаем директорию если не существует
        os.makedirs(upload_dir, exist_ok=True)
        
        # Генерируем уникальное имя файла
        file_ext = upload_file.filename.split('.')[-1] if '.' in upload_file.filename else 'jpg'
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_ext}"
        filepath = os.path.join(upload_dir, filename)
        
        # Сохраняем файл
        with open(filepath, "wb") as buffer:
            content = upload_file.file.read()
            buffer.write(content)
        
        return filepath
    except Exception as e:
        print(f"Ошибка сохранения файла: {e}")
        return None

def draw_detections_on_image(image_bytes: bytes, detections: dict) -> bytes:
    """Рисует bounding boxes на изображении"""
    try:
        # Загружаем изображение
        image = Image.open(io.BytesIO(image_bytes))
        draw = ImageDraw.Draw(image)
        
        # Простые bounding boxes для цветовой детекции
        if 'detected_fruits' in detections:
            for fruit_data in detections['detected_fruits']:
                if isinstance(fruit_data, dict) and 'boxes' in fruit_data:
                    for box in fruit_data['boxes']:
                        if all(k in box for k in ['x', 'y', 'width', 'height']):
                            # Рисуем прямоугольник
                            draw.rectangle(
                                [(box['x'], box['y']), 
                                 (box['x'] + box['width'], box['y'] + box['height'])],
                                outline='green',
                                width=2
                            )
                            # Подпись
                            fruit_type = fruit_data.get('fruit_type', 'fruit')
                            draw.text(
                                (box['x'], box['y'] - 10),
                                fruit_type,
                                fill='green'
                            )
        
        # Сохраняем в bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
        
    except Exception as e:
        print(f"Ошибка при рисовании детекций: {e}")
        return image_bytes

def validate_image_file(file) -> tuple[bool, str]:
    """Проверяет валидность загружаемого изображения"""
    # Проверяем размер файла (максимум 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    
    # Читаем начало файла для проверки
    file.file.seek(0, 2)  # Переходим в конец
    file_size = file.file.tell()
    file.file.seek(0)  # Возвращаемся в начало
    
    if file_size > max_size:
        return False, f"Файл слишком большой. Максимальный размер: {max_size // (1024*1024)}MB"
    
    # Проверяем тип файла
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        return False, f"Неподдерживаемый тип файла. Разрешены: {', '.join(allowed_types)}"
    
    return True, "OK"