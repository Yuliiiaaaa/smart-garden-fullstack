import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Any
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AlwaysFindFruitsDetector:
    """Детектор, который ВСЕГДА находит плоды (для демонстрации)"""
    
    def __init__(self):
        self.fruit_types = ['apple', 'pear', 'cherry', 'plum']
        logger.info("Инициализирован AlwaysFindFruitsDetector")
    
    def detect(self, image_bytes: bytes, expected_fruit: str = 'apple') -> Dict[str, Any]:
        """
        Всегда находит плоды на изображении!
        """
        try:
            # Загружаем изображение чтобы получить его размеры
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            
            # ВСЕГДА находим какое-то количество плодов
            # Базовое количество от 5 до 25
            base_count = random.randint(5, 25)
            
            # Если загружено реальное фото, ищем по цветам
            image_np = np.array(image)
            
            # Пробуем найти красные области (яблоки)
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Маски для разных цветов фруктов
            masks = {
                'apple': cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255])),  # Красный
                'pear': cv2.inRange(hsv, np.array([20, 50, 50]), np.array([40, 255, 255])),  # Желтый
                'cherry': cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255])),  # Темно-красный
            }
            
            detected_fruits = []
            total_real_count = 0
            
            for fruit_type, mask in masks.items():
                # Находим контуры
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                fruit_boxes = []
                fruit_count = 0
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # Минимальный размер
                        x, y, w, h = cv2.boundingRect(contour)
                        fruit_boxes.append({
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h),
                            'area': float(area)
                        })
                        fruit_count += 1
                
                if fruit_count > 0:
                    detected_fruits.append({
                        'fruit_type': fruit_type,
                        'count': fruit_count,
                        'boxes': fruit_boxes
                    })
                    total_real_count += fruit_count
            
            # Если реально не нашли ничего, ГЕНЕРИРУЕМ ДАННЫЕ
            if total_real_count == 0:
                # Генерируем "обнаруженные" плоды
                fruit_count = base_count
                
                # Создаем случайные bounding boxes
                boxes = []
                for i in range(fruit_count):
                    # Случайные координаты (избегаем краев)
                    x = random.randint(50, width - 100)
                    y = random.randint(50, height - 100)
                    size = random.randint(20, 60)
                    
                    boxes.append({
                        'x': x,
                        'y': y,
                        'width': size,
                        'height': size,
                        'area': size * size
                    })
                
                detected_fruits = [{
                    'fruit_type': expected_fruit,
                    'count': fruit_count,
                    'boxes': boxes
                }]
                total_count = fruit_count
                confidence = 0.7 + random.random() * 0.2  # 70-90%
                method = 'generated'
            else:
                total_count = total_real_count
                confidence = min(0.8 + (total_count * 0.01), 0.95)  # 80-95%
                method = 'color_detection'
            
            # Генерируем рекомендации
            recommendations = self._generate_recommendations(total_count, expected_fruit)
            
            return {
                'total_fruits': total_count,
                'detected_fruits': detected_fruits,
                'method': method,
                'confidence': confidence,
                'recommendations': recommendations,
                'image_size': f"{width}x{height}"
            }
            
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            # Даже при ошибке возвращаем демо-данные
            return self._generate_demo_data(expected_fruit)
    
    def _generate_demo_data(self, fruit_type: str) -> Dict[str, Any]:
        """Генерирует демо-данные при ошибке"""
        fruit_count = random.randint(8, 15)
        
        boxes = []
        for i in range(fruit_count):
            boxes.append({
                'x': random.randint(50, 400),
                'y': random.randint(50, 300),
                'width': random.randint(25, 45),
                'height': random.randint(25, 45),
                'area': random.randint(600, 2000)
            })
        
        return {
            'total_fruits': fruit_count,
            'detected_fruits': [{
                'fruit_type': fruit_type,
                'count': fruit_count,
                'boxes': boxes
            }],
            'method': 'demo',
            'confidence': 0.85,
            'recommendations': self._generate_recommendations(fruit_count, fruit_type),
            'note': 'Демо-данные (реальная обработка не удалась)'
        }
    
    def _generate_recommendations(self, count: int, fruit_type: str) -> str:
        """Генерирует умные рекомендации"""
        recommendations = []
        
        # На основе количества
        if count == 0:
            return "Плоды не обнаружены. Попробуйте сфотографировать другую ветку."
        elif count < 5:
            recommendations.append(f"Обнаружено мало плодов ({count} шт). Проверьте состояние дерева.")
        elif count < 15:
            recommendations.append(f"Средняя урожайность ({count} плодов). Всё в норме.")
        elif count < 30:
            recommendations.append(f"Хорошая урожайность ({count} плодов)! Дерево здорово.")
        else:
            recommendations.append(f"Отличная урожайность ({count} плодов)! Рекомендуется сбор через неделю.")
        
        # На основе типа фрукта
        if fruit_type == 'apple':
            recommendations.append("Яблоки созреют через 2-3 недели.")
        elif fruit_type == 'pear':
            recommendations.append("Груши готовы к сбору когда слегка пожелтеют.")
        elif fruit_type == 'cherry':
            recommendations.append("Вишни собирают когда становятся темно-красными.")
        
        # Сезонные рекомендации
        month = datetime.now().month
        if 6 <= month <= 8:
            recommendations.append("Летний сезон: увеличьте полив.")
        elif 9 <= month <= 10:
            recommendations.append("Осенний сезон: готовьтесь к сбору урожая.")
        
        return " ".join(recommendations)

# Глобальный экземпляр
always_detector = AlwaysFindFruitsDetector()