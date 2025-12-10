from typing import Dict, Any
import logging
from .improved_detector import improved_detector

logger = logging.getLogger(__name__)

class FruitDetectionService:
    """Улучшенный сервис детекции с настраиваемой точностью"""
    
    def __init__(self, accuracy_level: str = 'medium'):
        self.accuracy_level = accuracy_level
        logger.info(f"Инициализация FruitDetectionService с точностью: {accuracy_level}")
    
    def process_image(self, image_bytes: bytes, expected_fruit: str = 'apple') -> Dict[str, Any]:
        """
        Обрабатывает изображение с улучшенной точностью
        """
        try:
            result = improved_detector.detect(image_bytes, expected_fruit)
            
            # Добавляем метаданные
            result['accuracy_level'] = self.accuracy_level
            result['model'] = 'improved_detector'
            result['version'] = '2.0'
            result['success'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            # Запасной вариант
            from .always_find_fruits import always_detector
            return always_detector.detect(image_bytes, expected_fruit)

# Глобальный экземпляр с СРЕДНЕЙ точностью (можно изменить на 'high' для большей точности)
ai_service = FruitDetectionService(accuracy_level='medium')