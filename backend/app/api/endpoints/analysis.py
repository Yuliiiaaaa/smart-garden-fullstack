from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime
import io  # Добавляем импорт io

from app.models.database import get_db, User, Tree, HarvestRecord
from app.models.schemas import AnalysisResult  # Теперь должен работать
from app.api.dependencies import get_current_user
from app.services.ai_service import ai_service
from app.utils.image_utils import save_uploaded_file, draw_detections_on_image, validate_image_file

router = APIRouter()

# Создаем директорию для загрузок
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/photo", response_model=AnalysisResult)
async def analyze_photo(
    file: UploadFile = File(...),
    tree_id: Optional[int] = None,
    fruit_type: str = "apple",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Анализ фотографии для подсчета плодов с использованием ИИ"""
    
    # Валидация файла
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Проверяем tree_id если указан
    tree = None
    if tree_id:
        tree = db.query(Tree).filter(Tree.id == tree_id).first()
        if not tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Дерево с ID {tree_id} не найдено"
            )
    
    try:
        # Читаем содержимое файла
        contents = await file.read()
        
        # Обрабатываем изображение с помощью ИИ
        start_time = datetime.now()
        detection_result = ai_service.process_image(contents)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Создаем изображение с детекциями
        annotated_image = draw_detections_on_image(contents, detection_result)
        
        # Сохраняем файл
        filepath = save_uploaded_file(file, UPLOAD_DIR)
        
        # Создаем запись в базе данных
        harvest_record = HarvestRecord(
            tree_id=tree_id or 0,
            fruit_count=detection_result['total_fruits'],
            image_path=filepath,
            confidence_score=detection_result.get('confidence', 0.0)
        )
        
        db.add(harvest_record)
        db.commit()
        db.refresh(harvest_record)
        
        # Форматируем результат
        detected_list = []
        if 'detected_fruits' in detection_result:
            if isinstance(detection_result['detected_fruits'], dict):
                for fruit_type, fruit_data in detection_result['detected_fruits'].items():
                    detected_list.append({
                        "fruit_type": fruit_type,
                        "count": fruit_data.get('count', 0),
                        "confidence": fruit_data.get('avg_confidence', 0.0),
                        "boxes": fruit_data.get('boxes', [])
                    })
            elif isinstance(detection_result['detected_fruits'], list):
                detected_list = detection_result['detected_fruits']
        
        return AnalysisResult(
            fruit_count=detection_result['total_fruits'],
            confidence=detection_result.get('confidence', 0.0),
            processing_time=processing_time,
            detected_fruits=detected_list,
            recommendations=detection_result.get('recommendations', ''),
            record_id=harvest_record.id,
            method=detection_result.get('method', 'unknown'),
            model=detection_result.get('model', 'simple')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )

@router.get("/history")
async def get_analysis_history(
    tree_id: Optional[int] = None,
    garden_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить историю анализов"""
    try:
        query = db.query(HarvestRecord)
        
        if tree_id:
            query = query.filter(HarvestRecord.tree_id == tree_id)
        elif garden_id:
            # Находим все деревья в саду
            from app.models.database import Tree
            tree_ids = db.query(Tree.id).filter(Tree.garden_id == garden_id).all()
            tree_ids = [tid[0] for tid in tree_ids]
            query = query.filter(HarvestRecord.tree_id.in_(tree_ids))
        
        records = query.order_by(HarvestRecord.harvest_date.desc()).limit(limit).all()
        
        return {
            "analyses": [
                {
                    "id": record.id,
                    "tree_id": record.tree_id,
                    "harvest_date": record.harvest_date.isoformat() if record.harvest_date else None,
                    "fruit_count": record.fruit_count,
                    "confidence": record.confidence_score,
                    "image_url": f"/uploads/{os.path.basename(record.image_path)}" if record.image_path else None
                }
                for record in records
            ],
            "total": len(records)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории: {str(e)}"
        )

@router.get("/demo")
async def demo_analysis():
    """Демонстрационный эндпоинт для тестирования ИИ"""
    try:
        # Создаем тестовое изображение (симуляция)
        import numpy as np
        from PIL import Image
        
        # Создаем простое тестовое изображение
        img_array = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        
        # Конвертируем в bytes
        img = Image.fromarray(img_array)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        
        # Обрабатываем
        result = ai_service.process_image(img_bytes)
        
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

@router.post("/calibrate")
async def calibrate_detector(
    file: UploadFile = File(...),
    expected_count: int = Form(...),
    fruit_type: str = Form("apple"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Калибровка детектора для более точного подсчета"""
    try:
        # Проверяем файл
        is_valid, error_msg = validate_image_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Читаем файл
        contents = await file.read()
        
        # Калибруем детектор
        from app.services.ai_service import ai_service
        calibration_factor = ai_service.calibrate_detector(contents, expected_count, fruit_type)
        
        # Анализируем с новыми настройками
        result = ai_service.process_image(contents, fruit_type)
        
        return {
            "calibration_success": True,
            "expected_count": expected_count,
            "detected_count": result['total_fruits'],
            "calibration_factor": calibration_factor,
            "message": f"Детектор откалиброван. Фактор: {calibration_factor:.3f}",
            "new_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка калибровки: {str(e)}")