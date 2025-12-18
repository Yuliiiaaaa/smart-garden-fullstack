# app/api/endpoints/analysis.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from app.models.database import get_db, User, Tree, HarvestRecord
from app.models.schemas import AnalysisResult
from app.api.dependencies import get_current_user
from app.services.ai_service import ai_service
from app.utils.image_utils import save_uploaded_file, validate_image_file

router = APIRouter()

# Создаем директорию для загрузок
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/photo", response_model=AnalysisResult)
async def analyze_photo(
    file: UploadFile = File(...),
    tree_id: Optional[int] = None,
    fruit_type: str = "apple",
    garden_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Анализ фотографии для подсчета плодов с использованием ИИ"""
    
    print(f" Анализ фото от пользователя: {current_user.email} (ID: {current_user.id})")
    
    # Валидация файла
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    try:
        # Читаем содержимое файла
        contents = await file.read()
        
        # Обрабатываем изображение с помощью ИИ
        start_time = datetime.now()
        detection_result = ai_service.process_image(contents, fruit_type)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Сохраняем файл
        filepath = save_uploaded_file(file, UPLOAD_DIR)
        
        print(f" Результат ИИ: {detection_result.get('total_fruits', 0)} плодов, уверенность: {detection_result.get('confidence', 0)}")
        
        # Создаем запись в базе данных (используем ОБНОВЛЕННУЮ модель)
        harvest_record = HarvestRecord(
            tree_id=tree_id,
            garden_id=garden_id,
            fruit_count=detection_result.get('total_fruits', 0),
            fruit_type=fruit_type,
            image_path=filepath,
            confidence_score=detection_result.get('confidence', 0.0),
            processing_time=processing_time,
            user_id=current_user.id  # Сохраняем ID пользователя
        )
        
        db.add(harvest_record)
        db.commit()
        db.refresh(harvest_record)
        
        print(f" Запись сохранена в БД: ID={harvest_record.id}, плодов={harvest_record.fruit_count}")
        
        # Форматируем результат для ответа
        detected_list = []
        if 'detected_fruits' in detection_result:
            if isinstance(detection_result['detected_fruits'], list):
                detected_list = detection_result['detected_fruits']
            elif isinstance(detection_result['detected_fruits'], dict):
                for ft, fruit_data in detection_result['detected_fruits'].items():
                    if isinstance(fruit_data, dict):
                        detected_list.append({
                            "fruit_type": ft,
                            "count": fruit_data.get('count', 0),
                            "confidence": fruit_data.get('confidence', fruit_data.get('avg_confidence', detection_result.get('confidence', 0.0))),  # Берем из разных мест
                            "boxes": fruit_data.get('boxes', [])
                        })

        # Если detected_list пуст, создаем базовую запись
        if not detected_list and detection_result.get('total_fruits', 0) > 0:
            detected_list = [{
                "fruit_type": fruit_type,
                "count": detection_result.get('total_fruits', 0),
                "confidence": detection_result.get('confidence', 0.0),
                "boxes": []
            }]

        # Также убедитесь что confidence есть во всех элементах
        for item in detected_list:
            if 'confidence' not in item:
                item['confidence'] = detection_result.get('confidence', 0.0)
        
        return AnalysisResult(
            fruit_count=detection_result.get('total_fruits', 0),
            confidence=detection_result.get('confidence', 0.0),
            processing_time=processing_time,
            detected_fruits=detected_list,
            recommendations=detection_result.get('recommendations', ''),
            record_id=harvest_record.id,
            method=detection_result.get('method', 'unknown'),
            model=detection_result.get('model', 'simple'),
            image_url=f"/uploads/{os.path.basename(filepath)}" if filepath else None
        )
        
    except Exception as e:
        print(f" Ошибка анализа: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )

@router.get("/history")
async def get_analysis_history(
    garden_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить историю анализов текущего пользователя"""
    try:
        print(f" Получение истории для пользователя: {current_user.email} (ID: {current_user.id})")
        
        # Запрос только записей текущего пользователя
        query = db.query(HarvestRecord).filter(HarvestRecord.user_id == current_user.id)
        
        if garden_id:
            query = query.filter(HarvestRecord.garden_id == garden_id)
        
        # Сортируем по дате (новые сначала)
        records = query.order_by(HarvestRecord.harvest_date.desc()).limit(limit).all()
        
        print(f" Найдено записей: {len(records)}")
        
        # Получаем информацию о садах для названий
        from app.models.database import Garden
        
        analyses = []
        for record in records:
            garden_name = "Не указан"
            if record.garden_id:
                garden = db.query(Garden).filter(Garden.id == record.garden_id).first()
                if garden:
                    garden_name = garden.name
            
            # Форматируем дату
            display_date = record.harvest_date or record.created_at
            if display_date:
                display_date_str = display_date.strftime("%d.%m.%Y, %H:%M")
            else:
                display_date_str = "Неизвестно"
            
            analyses.append({
                "id": record.id,
                "tree_id": record.tree_id,
                "garden_id": record.garden_id,
                "garden_name": garden_name,
                "fruit_type": record.fruit_type or "apple",
                "harvest_date": display_date_str,
                "fruit_count": record.fruit_count or 0,
                "confidence": record.confidence_score or 0.0,
                "processing_time": record.processing_time or 0.0,
                "image_url": f"/uploads/{os.path.basename(record.image_path)}" if record.image_path else None,
                "created_at": record.created_at.isoformat() if record.created_at else None
            })
        
        return {
            "analyses": analyses,
            "total": len(analyses),
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "role": current_user.role
            }
        }
        
    except Exception as e:
        print(f" Ошибка получения истории: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории: {str(e)}"
        )

@router.get("/demo")
async def demo_analysis():
    """Демонстрационный эндпоинт для тестирования ИИ"""
    try:
        import numpy as np
        from PIL import Image
        import io
        
        # Создаем простое тестовое изображение
        img_array = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        
        # Конвертируем в bytes
        img = Image.fromarray(img_array)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        
        # Обрабатываем
        result = ai_service.process_image(img_bytes, "apple")
        
        return {
            "message": "Демонстрационный анализ",
            "result": result,
            "note": "Это тестовый результат на случайном изображении"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка демо: {str(e)}"
        )