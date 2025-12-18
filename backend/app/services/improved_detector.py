import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Tuple
import logging
import math
import json

logger = logging.getLogger(__name__)

class NumpyEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для numpy типов"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        return super().default(obj)

class ImprovedFruitDetector:
    """Улучшенный детектор фруктов с мульти-методной детекцией"""
    
    def __init__(self, accuracy_level: str = 'high'):
        """
        accuracy_level: 
        - 'low': быстрая детекция (меньшая точность)
        - 'medium': баланс скорости и точности
        - 'high': максимальная точность (медленнее)
        """
        self.accuracy_level = accuracy_level
        self.fruit_colors = self._get_color_ranges()
        logger.info(f"Инициализирован ImprovedFruitDetector с уровнем точности: {accuracy_level}")
    
    def _convert_numpy_types(self, obj):
        """Рекурсивно преобразует numpy типы в нативные Python типы"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj
    
    def _get_color_ranges(self) -> Dict:
        """Расширенные диапазоны цветов для разных фруктов"""
        return {
            'apple': {
                'hsv_ranges': [
                    # Красные яблоки (диапазон 1)
                    (np.array([0, 100, 80]), np.array([10, 255, 255])),
                    # Красные яблоки (диапазон 2 - другая сторона спектра)
                    (np.array([170, 100, 80]), np.array([180, 255, 255])),
                    # Зеленые яблоки
                    (np.array([35, 40, 40]), np.array([85, 255, 200])),
                ],
                'lab_ranges': [
                    # Яблоки в LAB пространстве
                    (np.array([20, 120, 120]), np.array([255, 150, 200])),
                ],
                'min_size': 200,     # Минимальный размер в пикселях
                'max_size': 8000,    # Максимальный размер
                'expected_size': 3000, # Ожидаемый средний размер
                'shape_factor': 0.6, # Коэффициент круглости
            },
            'pear': {
                'hsv_ranges': [
                    # Желтые/зеленые груши
                    (np.array([20, 40, 60]), np.array([45, 200, 220])),
                ],
                'lab_ranges': [
                    (np.array([50, 120, 140]), np.array([200, 140, 180])),
                ],
                'min_size': 300,
                'max_size': 10000,
                'expected_size': 4000,
                'shape_factor': 0.5,  # Груши менее круглые
            },
            'cherry': {
                'hsv_ranges': [
                    # Вишни (темно-красные)
                    (np.array([0, 120, 50]), np.array([10, 255, 180])),
                    (np.array([170, 120, 50]), np.array([180, 255, 180])),
                ],
                'lab_ranges': [
                    (np.array([10, 140, 150]), np.array([60, 180, 200])),
                ],
                'min_size': 50,      # Вишни меньше
                'max_size': 2000,
                'expected_size': 800,
                'shape_factor': 0.7,
            },
            'plum': {
                'hsv_ranges': [
                    # Сливы (фиолетовые/синие)
                    (np.array([110, 40, 40]), np.array([140, 255, 200])),
                ],
                'lab_ranges': [
                    (np.array([30, 130, 150]), np.array([80, 170, 200])),
                ],
                'min_size': 150,
                'max_size': 5000,
                'expected_size': 2000,
                'shape_factor': 0.65,
            }
        }
    
    def _preprocess_image(self, image_np: np.ndarray) -> np.ndarray:
        """Предобработка изображения для улучшения детекции"""
        # 1. Увеличиваем контраст
        lab = cv2.cvtColor(image_np, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Применяем CLAHE к L-каналу
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Объединяем обратно
        limg = cv2.merge([cl, a, b])
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
        
        # 2. Увеличиваем насыщенность (только для высокого уровня точности)
        if self.accuracy_level == 'high':
            hsv = cv2.cvtColor(enhanced, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)
            s = cv2.add(s, 30)
            v = cv2.add(v, 20)
            enhanced = cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2RGB)
        
        # 3. Гауссово размытие для уменьшения шума
        if self.accuracy_level != 'low':
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        return enhanced
    
    def _detect_by_color(self, image: np.ndarray, fruit_type: str) -> np.ndarray:
        """Детекция по цвету в нескольких цветовых пространствах"""
        if fruit_type not in self.fruit_colors:
            fruit_type = 'apple'
        
        color_info = self.fruit_colors[fruit_type]
        combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        # 1. Детекция в HSV пространстве
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        for lower, upper in color_info['hsv_ranges']:
            mask = cv2.inRange(hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # 2. Детекция в LAB пространстве (только для среднего и высокого уровней)
        if self.accuracy_level in ['medium', 'high']:
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            for lower, upper in color_info.get('lab_ranges', []):
                mask = cv2.inRange(lab, lower, upper)
                combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Улучшение маски
        kernel_size = 3 if self.accuracy_level == 'low' else 5
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        
        # Морфологические операции для очистки маски
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        
        # Удаление мелких объектов
        if self.accuracy_level != 'low':
            # Находим все контуры
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Создаем чистую маску
            clean_mask = np.zeros_like(combined_mask)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > color_info['min_size'] / 2:  # Более мягкий фильтр
                    cv2.drawContours(clean_mask, [contour], -1, 255, -1)
            
            combined_mask = clean_mask
        
        return combined_mask
    


    def _detect_by_circles(self, image: np.ndarray, mask: np.ndarray, fruit_type: str) -> List[Dict]:
        """Детекция круглых объектов (плодов)"""
        if fruit_type not in self.fruit_colors:
            fruit_type = 'apple'
        
        color_info = self.fruit_colors[fruit_type]
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Применяем маску
        gray_masked = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Определяем параметры для HoughCircles в зависимости от фрукта
        if fruit_type == 'cherry':
            min_radius = 5
            max_radius = 25
            dp = 1.2
        elif fruit_type == 'apple':
            min_radius = 15
            max_radius = 50
            dp = 1.5
        elif fruit_type == 'pear':
            min_radius = 20
            max_radius = 60
            dp = 1.5
        else:  # plum
            min_radius = 10
            max_radius = 40
            dp = 1.3
        
        # Детекция кругов только для среднего и высокого уровней
        if self.accuracy_level in ['medium', 'high']:
            circles = cv2.HoughCircles(
                gray_masked,
                cv2.HOUGH_GRADIENT,
                dp=dp,
                minDist=min_radius * 2,
                param1=50,
                param2=30 if self.accuracy_level == 'high' else 25,
                minRadius=min_radius,
                maxRadius=max_radius
            )
        else:
            circles = None
        
        detected_circles = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
                # ИСПРАВЛЕНО: проверяем чтобы координаты не выходили за границы
                x_pos = max(0, x - r)
                y_pos = max(0, y - r)
                width = r * 2
                height = r * 2
                
                # Проверяем чтобы не выходило за границы изображения
                height_img, width_img = image.shape[:2]
                if x_pos + width <= width_img and y_pos + height <= height_img:
                    detected_circles.append({
                        'x': x_pos,
                        'y': y_pos,
                        'width': width,
                        'height': height,
                        'radius': r,
                        'center': (x, y)
                    })
        
        return detected_circles
    
    def _detect_by_contours(self, mask: np.ndarray, fruit_type: str) -> List[Dict]:
        """Детекция по контурам с фильтрацией по форме"""
        if fruit_type not in self.fruit_colors:
            fruit_type = 'apple'
        
        color_info = self.fruit_colors[fruit_type]
        
        # Находим контуры
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Фильтрация по размеру
            if area < color_info['min_size'] or area > color_info['max_size']:
                continue
            
            # Вычисляем параметры формы
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            # Круглость
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # Соотношение сторон bounding box
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h > 0 else 1
            
            # Фильтрация по форме (зависит от типа фрукта)
            min_circularity = color_info['shape_factor'] - 0.2
            max_circularity = color_info['shape_factor'] + 0.4
            
            if min_circularity < circularity < max_circularity and 0.5 < aspect_ratio < 2.0:
                detected_contours.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': float(area),
                    'circularity': float(circularity)
                })
        
        return detected_contours
    
    def _merge_detections(self, circles: List[Dict], contours: List[Dict]) -> List[Dict]:
        """Объединение дублирующихся детекций"""
        all_detections = []
        
        # Преобразуем круги в формат bounding boxes
        circle_boxes = []
        for circle in circles:
            circle_boxes.append({
                'x': circle['x'],
                'y': circle['y'],
                'width': circle['width'],
                'height': circle['height'],
                'type': 'circle',
                'data': circle
            })
        
        # Преобразуем контуры в формат bounding boxes
        contour_boxes = []
        for contour in contours:
            contour_boxes.append({
                'x': contour['x'],
                'y': contour['y'],
                'width': contour['width'],
                'height': contour['height'],
                'type': 'contour',
                'data': contour
            })
        
        # Объединяем все детекции
        all_boxes = circle_boxes + contour_boxes
        
        # Удаляем дубликаты (близко расположенные bounding boxes)
        merged_boxes = []
        used = [False] * len(all_boxes)
        
        for i, box1 in enumerate(all_boxes):
            if used[i]:
                continue
            
            # Находим центр первого бокса
            cx1 = box1['x'] + box1['width'] / 2
            cy1 = box1['y'] + box1['height'] / 2
            
            # Ищем перекрывающиеся боксы
            merged_box = box1.copy()
            count = 1
            
            for j in range(i + 1, len(all_boxes)):
                if used[j]:
                    continue
                
                box2 = all_boxes[j]
                cx2 = box2['x'] + box2['width'] / 2
                cy2 = box2['y'] + box2['height'] / 2
                
                # Расстояние между центрами
                distance = math.sqrt((cx2 - cx1)**2 + (cy2 - cy1)**2)
                
                # Если боксы близко (перекрываются), объединяем
                max_dimension = max(box1['width'], box1['height'], box2['width'], box2['height'])
                if distance < max_dimension * 0.7:
                    # Объединяем координаты (взвешенное среднее)
                    merged_box['x'] = (merged_box['x'] * count + box2['x']) / (count + 1)
                    merged_box['y'] = (merged_box['y'] * count + box2['y']) / (count + 1)
                    merged_box['width'] = (merged_box['width'] * count + box2['width']) / (count + 1)
                    merged_box['height'] = (merged_box['height'] * count + box2['height']) / (count + 1)
                    used[j] = True
                    count += 1
            
            merged_boxes.append(merged_box)
            used[i] = True
        
        # Конвертируем обратно в формат результата
        result = []
        for box in merged_boxes:
            result.append({
                'x': int(box['x']),
                'y': int(box['y']),
                'width': int(box['width']),
                'height': int(box['height']),
                'area': float(box['width'] * box['height'])
            })
        
        return result
    
    def _calculate_confidence(self, detections: List[Dict], image_area: int, fruit_type: str) -> float:
        """Расчет уверенности в результатах"""
        if fruit_type not in self.fruit_colors:
            fruit_type = 'apple'
        
        color_info = self.fruit_colors[fruit_type]
        
        if not detections:
            return 0.3  # Низкая уверенность если ничего не найдено
        
        # 1. Уверенность на основе количества обнаружений
        count_confidence = min(len(detections) / 10, 1.0) * 0.3
        
        # 2. Уверенность на основе размера объектов
        size_confidence = 0.0
        total_area = 0
        
        for det in detections:
            area = det['area']
            total_area += area
            
            # Проверяем соответствие ожидаемому размеру
            size_diff = abs(area - color_info['expected_size']) / color_info['expected_size']
            if size_diff < 0.5:  # В пределах 50% от ожидаемого
                size_confidence += 0.1
        
        size_confidence = min(size_confidence / len(detections), 0.3)
        
        # 3. Уверенность на основе распределения объектов
        distribution_confidence = 0.0
        if len(detections) > 1:
            # Проверяем что объекты не все в одном месте
            centers = []
            for det in detections:
                centers.append((det['x'] + det['width']/2, det['y'] + det['height']/2))
            
            # Вычисляем среднее расстояние между центрами
            total_distance = 0
            count = 0
            for i in range(len(centers)):
                for j in range(i+1, len(centers)):
                    dx = centers[i][0] - centers[j][0]
                    dy = centers[i][1] - centers[j][1]
                    total_distance += math.sqrt(dx*dx + dy*dy)
                    count += 1
            
            if count > 0:
                avg_distance = total_distance / count
                # Нормализуем по размеру изображения
                img_diagonal = math.sqrt(image_area)
                if avg_distance > img_diagonal * 0.05:  # Объекты достаточно разнесены
                    distribution_confidence = 0.2
        
        # 4. Базовый уровень уверенности в зависимости от accuracy_level
        base_confidence = {'low': 0.5, 'medium': 0.7, 'high': 0.8}[self.accuracy_level]
        
        # Итоговая уверенность
        confidence = base_confidence + count_confidence + size_confidence + distribution_confidence
        return min(confidence, 0.95)  # Максимум 95%
    
    def detect(self, image_bytes: bytes, expected_fruit: str = 'apple') -> Dict[str, Any]:
        """
        Основной метод детекции с несколькими алгоритмами
        """
        try:
            # Загружаем и декодируем изображение
            image_pil = Image.open(io.BytesIO(image_bytes))
            
            # Конвертируем в RGB если нужно (для JPEG)
            if image_pil.mode != 'RGB':
                image_pil = image_pil.convert('RGB')
            
            image_np = np.array(image_pil)
            height, width = image_np.shape[:2]
            image_area = width * height
            
            # Предобработка изображения
            processed_image = self._preprocess_image(image_np)
            
            # Детекция по цвету
            color_mask = self._detect_by_color(processed_image, expected_fruit)
            
            # Детекция кругов (для круглых фруктов)
            circles = self._detect_by_circles(processed_image, color_mask, expected_fruit)
            
            # Детекция по контурам
            contours = self._detect_by_contours(color_mask, expected_fruit)
            
            # Объединение результатов
            all_detections = self._merge_detections(circles, contours)
            
            # Если ничего не найдено, пробуем альтернативные методы
            if not all_detections and self.accuracy_level in ['medium', 'high']:
                # Пробуем найти контуры на оригинальном изображении
                gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Адаптивный порог
                thresh = cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV, 11, 2
                )
                
                # Находим контуры
                alt_contours, _ = cv2.findContours(
                    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                
                # Фильтруем по размеру
                for contour in alt_contours:
                    area = cv2.contourArea(contour)
                    if 200 < area < 5000:  # Базовые размеры плодов
                        x, y, w, h = cv2.boundingRect(contour)
                        all_detections.append({
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h),
                            'area': float(area)
                        })
            
            # Рассчитываем уверенность
            confidence = self._calculate_confidence(all_detections, image_area, expected_fruit)
            
            # Формируем результат
            result = {
                'total_fruits': len(all_detections),
                'detected_fruits': [{
                    'fruit_type': expected_fruit,
                    'count': len(all_detections),
                    'boxes': all_detections,
                    'sizes': [d['area'] for d in all_detections] if all_detections else []
                }],
                'method': 'multi_method',
                'model': 'improved_detector_v2',
                'accuracy_level': self.accuracy_level,
                'confidence': float(confidence),  # Явное преобразование в float
                'image_size': f"{width}x{height}",
                'timestamp': self._get_timestamp(),
                'recommendations': self._generate_recommendations(len(all_detections), expected_fruit),
            }
            
            # Добавляем отладочную информацию для высокого уровня
            if self.accuracy_level == 'high':
                result['debug_info'] = {
                    'circles_found': len(circles),
                    'contours_found': len(contours),
                    'merged_count': len(all_detections),
                    'image_area': int(image_area),  # Преобразуем в int
                }
            
            # Преобразуем все numpy типы в нативные Python типы
            result = self._convert_numpy_types(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка детекции: {e}")
            # Возвращаем минимальный результат вместо демо-данных
            return self._convert_numpy_types({
                'total_fruits': 0,
                'detected_fruits': [],
                'method': 'error_fallback',
                'model': 'improved_detector_v2',
                'accuracy_level': self.accuracy_level,
                'confidence': 0.1,
                'error': str(e),
                'recommendations': 'Ошибка обработки изображения. Попробуйте другое фото.',
            })
    
    def _get_timestamp(self) -> str:
        """Получение временной метки"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_recommendations(self, count: int, fruit_type: str) -> str:
        """Генерация рекомендаций на основе результатов"""
        recommendations = []
        
        if count == 0:
            recommendations.append("Плоды не обнаружены. Попробуйте:")
            recommendations.append("- Сфотографировать при лучшем освещении")
            recommendations.append("- Убедиться что плоды в кадре")
            recommendations.append("- Попробовать другой ракурс")
        elif count < 3:
            recommendations.append(f"Обнаружено мало плодов ({count} шт).")
            recommendations.append("Рекомендуется проверить состояние дерева.")
        elif count < 10:
            recommendations.append(f"Средняя урожайность: {count} плодов.")
            recommendations.append("Дерево в нормальном состоянии.")
        elif count < 20:
            recommendations.append(f"Хорошая урожайность: {count} плодов!")
            recommendations.append("Рекомендуется сбор через 1-2 недели.")
        else:
            recommendations.append(f"Отличная урожайность: {count} плодов!")
            recommendations.append("Рекомендуется сбор на этой неделе.")
        
        # Добавляем рекомендации по типу фрукта
        if fruit_type == 'apple':
            recommendations.append("Яблоки: оптимальный сбор при полном окрасе.")
        elif fruit_type == 'pear':
            recommendations.append("Груши: собирайте когда плодоножка легко отделяется.")
        elif fruit_type == 'cherry':
            recommendations.append("Вишни: собирайте полностью окрашенные плоды.")
        elif fruit_type == 'plum':
            recommendations.append("Сливы: спелые при легком нажатии.")
        
        return " ".join(recommendations)

# Глобальный экземпляр с ВЫСОКОЙ точностью
improved_detector = ImprovedFruitDetector(accuracy_level='high')