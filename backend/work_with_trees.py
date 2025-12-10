import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def work_with_trees():
    print("🌳 Работа с деревьями через API")
    print("=" * 50)
    
    # 1. Вход
    print("\n1. Вход в систему...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print(f"❌ Ошибка входа: {response.text}")
        return
    
    token_data = response.json()
    token = token_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Вход успешен. Токен получен.")
    
    # 2. Получить список садов
    print("\n2. Получаем список садов...")
    response = requests.get(f"{BASE_URL}/gardens/", headers=headers)
    
    if response.status_code == 200:
        gardens = response.json()
        print(f"✅ Найдено садов: {len(gardens)}")
        
        if gardens:
            # Берем первый сад
            garden_id = gardens[0]['id']
            garden_name = gardens[0]['name']
            print(f"   🏡 Используем сад: {garden_name} (ID: {garden_id})")
            
            # 3. Создать дерево
            print("\n3. Создаем новое дерево...")
            tree_data = {
                "garden_id": garden_id,
                "row_number": 1,
                "tree_number": 1,
                "variety": "Голден",
                "planting_year": 2020
            }
            
            response = requests.post(f"{BASE_URL}/trees/", 
                                   headers=headers, 
                                   json=tree_data)
            
            if response.status_code == 201:
                tree = response.json()
                print(f"✅ Дерево создано! ID: {tree['id']}")
                print(f"   📍 Ряд: {tree['row_number']}, Дерево: {tree['tree_number']}")
                print(f"   🍎 Сорт: {tree['variety']}")
                
                tree_id = tree['id']
            else:
                print(f"❌ Ошибка создания дерева: {response.status_code} - {response.text}")
                return
        else:
            print("❌ Нет садов. Создайте сначала сад.")
            return
    else:
        print(f"❌ Ошибка получения садов: {response.status_code} - {response.text}")
        return
    
    # 4. Получить список деревьев
    print("\n4. Получаем список всех деревьев...")
    response = requests.get(f"{BASE_URL}/trees/", headers=headers)
    
    if response.status_code == 200:
        trees = response.json()
        print(f"✅ Всего деревьев в системе: {len(trees)}")
        
        if trees:
            print("   📋 Список деревьев:")
            for tree in trees:
                print(f"      • ID {tree['id']}: ряд {tree['row_number']}, дерево {tree['tree_number']}")
    
    # 5. Сделать фото-анализ для дерева
    print("\n5. Тестируем анализ фото для дерева...")
    print("   📸 (Это симуляция - в реальности нужно загружать фото)")
    
    # 6. Получить деревья конкретного сада
    print(f"\n6. Деревья в саду ID {garden_id}:")
    response = requests.get(f"{BASE_URL}/trees/?garden_id={garden_id}", headers=headers)
    
    if response.status_code == 200:
        garden_trees = response.json()
        print(f"   🌲 Деревьев в этом саду: {len(garden_trees)}")
    
    return True

def test_all_endpoints():
    print("\n\n🔧 Тестирование всех защищенных эндпоинтов:")
    print("=" * 50)
    
    # Вход
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        return
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("GET", "/gardens/", "Список садов"),
        ("POST", "/gardens/", "Создание сада"),
        ("GET", "/trees/", "Список деревьев"),
        ("POST", "/trees/", "Создание дерева"),
        ("GET", "/analysis/history", "История анализов"),
        ("GET", "/analytics/overview", "Общая аналитика"),
        ("GET", "/auth/me", "Информация о пользователе"),
    ]
    
    for method, endpoint, description in endpoints:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST" and "gardens" in endpoint:
            # Создаем тестовый сад
            data = {
                "name": f"Тестовый сад {description}",
                "location": "Тест",
                "area": 1.0,
                "fruit_type": "apple"
            }
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
        elif method == "POST" and "trees" in endpoint:
            # Создаем тестовое дерево
            response = requests.get(f"{BASE_URL}/gardens/", headers=headers)
            if response.status_code == 200 and response.json():
                garden_id = response.json()[0]['id']
                data = {
                    "garden_id": garden_id,
                    "row_number": 99,
                    "tree_number": 99,
                    "variety": "Тестовый"
                }
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
            else:
                continue
        
        status_icon = "✅" if response.status_code in [200, 201] else "❌"
        print(f"{status_icon} {description}: {response.status_code}")

if __name__ == "__main__":
    print("=" * 70)
    print("          ПРАКТИЧЕСКАЯ РАБОТА С ДЕРЕВЬЯМИ")
    print("=" * 70)
    
    if work_with_trees():
        print("\n🎉 Отлично! Все операции с деревьями работают!")
    
    test_all_endpoints()
    
    print("\n" + "=" * 70)
    print("📋 Краткая инструкция для демонстрации проекта:")
    print("\n1. Запусти фронтенд: cd ../frontend && npm start")
    print("2. Открой браузер: http://localhost:3000")
    print("3. Войди в систему (admin@example.com / admin123)")
    print("4. Создай сад → добавь деревья → загрузи фото для анализа")
    print("5. Смотри аналитику и графики!")
    print("=" * 70)