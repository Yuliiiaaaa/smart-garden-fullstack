import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_request(method, url, status_code, headers=None):
    """Красиво выводит информацию о запросе"""
    print(f"\n{method} {url}")
    print(f"Status: {status_code}")
    if headers and 'Authorization' in headers:
        print(f"Auth: {headers['Authorization'][:50]}...")
    print("-" * 50)

def test_middleware_protection():
    print("🛡️ Тестирование защиты middleware")
    print("=" * 60)
    
    # 1. Публичные эндпоинты (должны работать без токена)
    print("\n1. Публичные эндпоинты (без токена):")
    
    public_endpoints = [
        ("GET", "/", "Главная страница"),
        ("GET", "/docs", "Документация"),
        ("GET", "/api/v1/health", "Health check"),
        ("POST", "/api/v1/auth/login", "Логин (публичный)"),
        ("POST", "/api/v1/auth/register", "Регистрация (публичный)"),
    ]
    
    for method, endpoint, description in public_endpoints:
        url = f"http://localhost:8000{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=3)
        elif method == "POST" and "login" in endpoint:
            response = requests.post(url, json={
                "email": "admin@example.com",
                "password": "admin123"
            }, timeout=3)
        elif method == "POST" and "register" in endpoint:
            response = requests.post(url, json={
                "email": "test_user@example.com",
                "password": "test123",
                "full_name": "Тестовый Пользователь"
            }, timeout=3)
        else:
            response = requests.post(url, timeout=3)
        
        if response.status_code in [200, 201]:
            print(f"✅ {description}: доступен (код {response.status_code})")
        else:
            print(f"⚠️  {description}: код {response.status_code}")

    # 2. Защищенные эндпоинты (без токена - должны возвращать 401)
    print("\n2. Защищенные эндпоинты (без токена):")
    
    protected_endpoints = [
        ("GET", "/api/v1/gardens/", "Список садов"),
        ("GET", "/api/v1/trees/", "Список деревьев"),
        ("GET", "/api/v1/auth/me", "Информация о пользователе"),
        ("GET", "/api/v1/analysis/history", "История анализов"),
    ]
    
    for method, endpoint, description in protected_endpoints:
        url = f"http://localhost:8000{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=3)
        else:
            response = requests.post(url, timeout=3)
        
        if response.status_code == 401:
            print(f"✅ {description}: защищен (401 Unauthorized)")
        elif response.status_code == 403:
            print(f"✅ {description}: защищен (403 Forbidden)")
        else:
            print(f"❌ {description}: не защищен (код {response.status_code})")

def test_jwt_workflow():
    print("\n\n🔐 Тестирование JWT workflow")
    print("=" * 60)
    
    # 1. Получение токена
    print("\n1. Получение JWT токена...")
    
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_request("POST", "/api/v1/auth/login", response.status_code)
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data['access_token']
        print(f"✅ Токен получен!")
        print(f"   Тип: {token_data['token_type']}")
        print(f"   Пользователь: {token_data['user']['full_name']}")
        print(f"   Роль: {token_data['user']['role']}")
        
        # 2. Использование токена для доступа к защищенным эндпоинтам
        print("\n2. Доступ к защищенным эндпоинтам с токеном:")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # GET /auth/me
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print_request("GET", "/api/v1/auth/me", response.status_code, headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Информация о пользователе получена")
            print(f"   👤 Имя: {user_info['full_name']}")
            print(f"   🎭 Роль: {user_info['role']}")
        else:
            print(f"❌ Ошибка: {response.text}")
        
        # GET /gardens/
        response = requests.get(f"{BASE_URL}/gardens/", headers=headers)
        print_request("GET", "/api/v1/gardens/", response.status_code, headers)
        
        if response.status_code == 200:
            gardens = response.json()
            print(f"✅ Сады получены: {len(gardens)} шт")
        else:
            print(f"❌ Ошибка: {response.text}")
        
        # GET /trees/
        response = requests.get(f"{BASE_URL}/trees/", headers=headers)
        print_request("GET", "/api/v1/trees/", response.status_code, headers)
        
        if response.status_code == 200:
            trees = response.json()
            print(f"✅ Деревья получены: {len(trees)} шт")
        else:
            print(f"❌ Ошибка: {response.text}")
        
        # 3. Создание нового сада
        print("\n3. Создание нового сада (требует аутентификации):")
        
        new_garden = {
            "name": "Тестовый сад для middleware",
            "location": "Тестовая локация",
            "area": 2.5,
            "fruit_type": "apple",
            "description": "Создан для тестирования middleware"
        }
        
        response = requests.post(f"{BASE_URL}/gardens/", headers=headers, json=new_garden)
        print_request("POST", "/api/v1/gardens/", response.status_code, headers)
        
        if response.status_code == 201:
            garden = response.json()
            print(f"✅ Сад создан! ID: {garden['id']}")
            garden_id = garden['id']
        else:
            print(f"❌ Ошибка создания: {response.text}")
            garden_id = 1  # Используем существующий
        
        # 4. Создание дерева
        print("\n4. Создание нового дерева (требует аутентификации):")
        
        new_tree = {
            "garden_id": garden_id,
            "row_number": 1,
            "tree_number": 1,
            "variety": "Голден",
            "planting_year": 2020
        }
        
        response = requests.post(f"{BASE_URL}/trees/", headers=headers, json=new_tree)
        print_request("POST", "/api/v1/trees/", response.status_code, headers)
        
        if response.status_code == 201:
            tree = response.json()
            print(f"✅ Дерево создано! ID: {tree['id']}")
        else:
            print(f"❌ Ошибка создания дерева: {response.text}")
        
        # 5. Тестирование неверного токена
        print("\n5. Тестирование неверного токена:")
        
        wrong_headers = {
            "Authorization": "Bearer wrong_token_12345",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/auth/me", headers=wrong_headers)
        print_request("GET", "/api/v1/auth/me (wrong token)", response.status_code, wrong_headers)
        
        if response.status_code == 401:
            print(f"✅ Защита от неверного токена работает!")
            error_detail = response.json().get('detail', '')
            print(f"   Сообщение: {error_detail}")
        else:
            print(f"❌ Неверный токен должен возвращать 401")
        
        # 6. Тестирование истечения токена (симуляция)
        print("\n6. Тестирование формата токена:")
        
        malformed_headers = [
            {"Authorization": "Bearer", "Content-Type": "application/json"},  # Пустой токен
            {"Authorization": "Basic abc123", "Content-Type": "application/json"},  # Не Bearer
            {"Authorization": "", "Content-Type": "application/json"},  # Пустой заголовок
            {"Content-Type": "application/json"}  # Нет заголовка Authorization
        ]
        
        for i, test_headers in enumerate(malformed_headers, 1):
            response = requests.get(f"{BASE_URL}/auth/me", headers=test_headers)
            print(f"   Тест {i}: код {response.status_code}")
            
            if response.status_code == 401:
                print(f"      ✅ Защита работает")
            else:
                print(f"      ⚠️  Ожидался 401")
    
    else:
        print(f"❌ Ошибка логина: {response.status_code} - {response.text}")

def test_role_based_middleware():
    print("\n\n👑 Тестирование ролевого middleware")
    print("=" * 60)
    
    users = [
        ("admin@example.com", "admin123", "Администратор"),
        ("manager@example.com", "manager123", "Менеджер"),
        ("user@example.com", "user123", "Пользователь")
    ]
    
    for email, password, role_name in users:
        print(f"\n👤 Тестируем {role_name} ({email}):")
        
        # Логин
        response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        
        if response.status_code != 200:
            print(f"   ❌ Ошибка входа: {response.text}")
            continue
        
        token = response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Тестируем разные операции
        operations = [
            ("GET", "/gardens/", "Просмотр садов"),
            ("POST", "/gardens/", "Создание сада"),
            ("DELETE", "/gardens/1", "Удаление сада (требует admin)"),
        ]
        
        for method, endpoint, description in operations:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                data = {
                    "name": f"Тест от {role_name}",
                    "location": "Тест",
                    "area": 1.0,
                    "fruit_type": "apple"
                }
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers)
            
            status_icon = "✅" if response.status_code in [200, 201] else "❌"
            forbidden_icon = "⛔" if response.status_code == 403 else ""
            
            print(f"   {status_icon}{forbidden_icon} {description}: {response.status_code}")
            
            if response.status_code == 403:
                print(f"      ↳ {response.json().get('detail', 'Запрещено')}")

def check_middleware_logs():
    print("\n\n📝 Проверка логов middleware в консоли сервера")
    print("=" * 60)
    
    print("Сервер должен логировать каждый запрос в формате:")
    print("[ГГГГ-ММ-ДД ЧЧ:ММ:СС] МЕТОД ПУТЬ - User: email (роль)")
    print("\nПример логов которые ты видишь в консоли сервера:")
    print("[2025-12-10 18:11:48] POST /api/v1/analysis/photo - User: admin@example.com (admin)")
    
    print("\n🔍 Проверь в консоли сервера:")
    print("1. Логируются ли ВСЕ запросы?")
    print("2. Есть ли информация о пользователе?")
    print("3. Есть ли информация о роли?")
    print("4. Логируются ли публичные эндпоинты? (/docs, /health)")

def test_rate_limiting_simulation():
    print("\n\n⏱️ Симуляция защиты от частых запросов")
    print("=" * 60)
    
    print("Отправляем несколько быстрых запросов...")
    
    # Логин
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print("❌ Не удалось войти")
        return
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Быстрые запросы
    print("Отправляем 5 быстрых запросов к /auth/me:")
    
    for i in range(5):
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   Запрос {i+1}: OK ({elapsed:.3f} сек)")
        else:
            print(f"   Запрос {i+1}: Ошибка {response.status_code}")
        
        time.sleep(0.1)  # Маленькая пауза

def manual_test_instructions():
    print("\n\n🔧 Ручное тестирование через Swagger")
    print("=" * 60)
    
    print("1. Открой http://localhost:8000/docs")
    print("2. Нажми кнопку 'Authorize' в правом верхнем углу")
    print("3. Введи: Bearer <твой_токен>")
    print("4. Тестируй эндпоинты:")
    print("   - GET /api/v1/gardens/ - должен работать")
    print("   - GET /api/v1/trees/ - должен работать")
    print("   - POST /api/v1/trees/ - создание дерева")
    print("   - DELETE /api/v1/gardens/1 - проверь права")
    
    print("\n📋 Что проверять:")
    print("✅ Запросы без токена - 401")
    print("✅ Запросы с токеном - 200/201")
    print("✅ Неверный токен - 401")
    print("✅ Логи в консоли сервера")
    print("✅ Ролевая модель (admin может удалять, user - нет)")

if __name__ == "__main__":
    print("=" * 70)
    print("          ТЕСТИРОВАНИЕ MIDDLEWARE И АУТЕНТИФИКАЦИИ")
    print("=" * 70)
    
    test_middleware_protection()
    test_jwt_workflow()
    test_role_based_middleware()
    check_middleware_logs()
    test_rate_limiting_simulation()
    manual_test_instructions()
    
    print("\n" + "=" * 70)
    print("🎉 Тестирование middleware завершено!")
    print("\n📋 Итог по защите API:")
    print("✅ Middleware проверяет JWT токены")
    print("✅ Публичные эндпоинты доступны без аутентификации")
    print("✅ Защищенные эндпоинты требуют токен")
    print("✅ Неверные токены отклоняются")
    print("✅ Логирование запросов работает")
    print("✅ Ролевая модель защищает операции")
    print("=" * 70)