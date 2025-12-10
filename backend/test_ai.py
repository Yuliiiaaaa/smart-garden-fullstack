import requests
import time
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json

BASE_URL = "http://localhost:8000/api/v1"

def create_realistic_fruit_image_with_count(target_count: int = 14):
    """Создает тестовое изображение с ЗАРАНЕЕ ИЗВЕСТНЫМ количеством плодов"""
    width, height = 800, 600
    
    # Фон - зеленая листва
    img = Image.new('RGB', (width, height), color=(34, 139, 34))
    draw = ImageDraw.Draw(img)
    
    # Ветки
    draw.line([(100, 100), (700, 150)], fill=(101, 67, 33), width=15)
    
    # Рисуем ТОЧНО target_count яблок
    fruits = []
    
    # Распределяем равномерно
    rows = int(np.sqrt(target_count)) + 1
    cols = (target_count + rows - 1) // rows
    
    cell_width = (width - 200) // cols
    cell_height = (height - 200) // rows
    
    for i in range(target_count):
        row = i // cols
        col = i % cols
        
        # Центр ячейки + небольшой случайный сдвиг
        x = 100 + col * cell_width + cell_width // 2 + np.random.randint(-30, 30)
        y = 100 + row * cell_height + cell_height // 2 + np.random.randint(-30, 30)
        size = np.random.randint(25, 40)
        
        # Цвет яблока (красный с вариациями)
        red = np.random.randint(200, 255)
        green = np.random.randint(0, 50)
        blue = np.random.randint(0, 50)
        
        # Рисуем яблоко
        draw.ellipse([x-size, y-size, x+size, y+size], 
                    fill=(red, green, blue), 
                    outline=(150, 0, 0))
        
        # Блик
        draw.ellipse([x-size//3, y-size//3, x-size//6, y-size//6], 
                    fill=(255, 255, 255, 128))
        
        fruits.append({
            'x': x - size,
            'y': y - size,
            'size': size * 2
        })
    
    # Подписываем количество
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), f"ТЕСТ: {target_count} яблок", fill=(255, 255, 255), font=font)
    
    # Сохраняем
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr, fruits

def test_with_exact_count():
    """Тест с ЗАРАНЕЕ ИЗВЕСТНЫМ количеством плодов"""
    print("🎯 Тест с известным количеством плодов")
    print("=" * 60)
    
    target_count = 14  # Точно 14 яблок!
    
    # 1. Создаем изображение
    print(f"\n1. Создаем изображение с {target_count} яблоками...")
    test_image, actual_fruits = create_realistic_fruit_image_with_count(target_count)
    
    # Сохраняем для просмотра
    with open(f"test_{target_count}_apples.jpg", "wb") as f:
        f.write(test_image.getvalue())
    print(f"💾 Изображение сохранено: test_{target_count}_apples.jpg")
    
    # 2. Авторизация
    print("\n2. Авторизация...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print("❌ Ошибка авторизации")
        return
    
    token_data = response.json()
    token = token_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Успешная авторизация")
    
    # 3. Анализ
    print(f"\n3. Анализ изображения (ожидаем ~{target_count} плодов)...")
    files = {"file": (f"test_{target_count}.jpg", test_image, "image/jpeg")}
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/analysis/photo",
        headers=headers,
        files=files,
        data={"fruit_type": "apple"}
    )
    processing_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        detected_count = result['fruit_count']
        error = abs(detected_count - target_count)
        error_percent = (error / target_count) * 100
        
        print(f"✅ Анализ завершен за {processing_time:.2f} сек")
        print(f"   🎯 Ожидалось: {target_count} плодов")
        print(f"   🍎 Обнаружено: {detected_count} плодов")
        print(f"   📊 Погрешность: {error} плодов ({error_percent:.1f}%)")
        print(f"   🎯 Уверенность: {result['confidence']:.2%}")
        print(f"   🤖 Метод: {result['method']}")
        
        # Оценка точности
        if error <= 2:
            print(f"   🏆 ТОЧНОСТЬ: ОТЛИЧНАЯ! (погрешность ≤ 2 плода)")
        elif error <= 5:
            print(f"   👍 ТОЧНОСТЬ: ХОРОШАЯ (погрешность ≤ 5 плодов)")
        elif error <= 10:
            print(f"   ⚠️  ТОЧНОСТЬ: СРЕДНЯЯ (погрешность ≤ 10 плодов)")
        else:
            print(f"   ❗ ТОЧНОСТЬ: НИЗКАЯ (погрешность > 10 плодов)")
        
        # Детали
        if 'debug_info' in result:
            print(f"   🔍 Детали: сырых обнаружений: {result['debug_info'].get('raw_detections', 'N/A')}")
        
        return result
    else:
        print(f"❌ Ошибка анализа: {response.status_code} - {response.text}")
        return None

def manual_correction_test():
    """Тест ручной коррекции результатов"""
    print("\n\n🛠️ Тест ручной коррекции")
    print("=" * 60)
    
    print("Если система считает неправильно (например, 45 вместо 14):")
    print("1. Можно использовать коэффициент коррекции")
    print("2. Или настроить детектор на меньшую чувствительность")
    
    correction_factors = {
        'очень чувствительный': 0.3,  # Находит много ложных срабатываний
        'чувствительный': 0.5,
        'средний': 0.7,  # По умолчанию
        'строгий': 0.9,
        'очень строгий': 1.2  # Может пропускать реальные плоды
    }
    
    print("\n📊 Коэффициенты коррекции для яблок:")
    for level, factor in correction_factors.items():
        print(f"   • {level}: ×{factor}")
    
    print("\n💡 Как исправить если считает 45 вместо 14:")
    print("   45 × 0.3 ≈ 13.5 (близко к 14!)")
    print("   Нужно уменьшить чувствительность детектора")

def test_different_accuracy_levels():
    """Тестирование разных уровней точности"""
    print("\n\n🔧 Тестирование разных уровней точности")
    print("=" * 60)
    
    # Импортируем детектор напрямую
    from app.services.improved_detector import ImprovedFruitDetector
    
    # Создаем тестовое изображение
    test_image, _ = create_realistic_fruit_image_with_count(14)
    image_bytes = test_image.getvalue()
    
    levels = ['low', 'medium', 'high']
    
    for level in levels:
        print(f"\nУровень точности: {level.upper()}")
        print("-" * 40)
        
        detector = ImprovedFruitDetector(accuracy_level=level)
        start_time = time.time()
        result = detector.detect(image_bytes, 'apple')
        processing_time = time.time() - start_time
        
        print(f"   Найдено плодов: {result['total_fruits']}")
        print(f"   Время: {processing_time:.2f} сек")
        print(f"   Метод: {result['method']}")
        print(f"   Уверенность: {result['confidence']:.2%}")

def create_calibration_tool():
    """Создает инструмент для калибровки"""
    print("\n\n🎛️ Инструмент для калибровки детектора")
    print("=" * 60)
    
    calibration_guide = """
    Как откалибровать детектор для ВАШЕГО сада:
    
    1. Сделайте 5-10 фото разных деревьев
    2. Вручную посчитайте плоды на каждом фото
    3. Запустите анализ через API
    4. Сравните результаты:
    
    Фото | Реально | Детектор | Коэффициент
    -----|---------|----------|------------
    #1   |   14    |    45    | 14/45 = 0.31
    #2   |   23    |    38    | 23/38 = 0.61
    #3   |   17    |    52    | 17/52 = 0.33
    
    5. Вычислите средний коэффициент: (0.31 + 0.61 + 0.33) / 3 = 0.42
    6. Установите этот коэффициент в детекторе!
    
    💡 Советы:
    • Используйте фото при одинаковом освещении
    • Избегайте бликов и теней
    • Фотографируйте с одинакового расстояния
    • Лучшее время: утро или вечер, пасмурная погода
    """
    
    print(calibration_guide)

if __name__ == "__main__":
    print("=" * 70)
    print("          УЛУЧШЕННЫЙ ИИ С НАСТРАИВАЕМОЙ ТОЧНОСТЬЮ")
    print("=" * 70)
    
    # Тест с известным количеством
    result = test_with_exact_count()
    
    # Демонстрация коррекции
    manual_correction_test()
    
    # Тест разных уровней точности
    test_different_accuracy_levels()
    
    # Инструмент калибровки
    create_calibration_tool()
    
    print("\n" + "=" * 70)
    print("🎯 КЛЮЧЕВЫЕ ВЫВОДЫ:")
    print("1. Текущая система может завышать количество в 2-3 раза")
    print("2. Это нормально для компьютерного зрения без обучения")
    print("3. Можно улучшить точность через калибровку")
    print("4. Для production нужна обученная модель на реальных фото")
    print("=" * 70)
    
    print("\n🚀 ЧТО ДЕЛАТЬ ДАЛЬШЕ:")
    print("1. Соберите реальные фото вашего сада")
    print("2. Протестируйте на них систему")
    print("3. Откалибруйте коэффициенты")
    print("4. Или дообучите YOLO на ваших данных")
    print("=" * 70)