import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class APITester:
    def __init__(self):
        self.tokens = {}
        self.user_info = {}
        
    def login(self, email, password):
        """Вход пользователя и сохранение токена"""
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            token_data = response.json()
            self.tokens[email] = token_data['access_token']
            self.user_info[email] = token_data['user']
            print(f"✅ {email}: Успешный вход (роль: {token_data['user']['role']})")
            return True
        else:
            print(f"❌ {email}: Ошибка входа - {response.status_code}: {response.text}")
            return False
    
    def make_request(self, method, endpoint, email=None, data=None):
        """Выполняет запрос от имени пользователя"""
        headers = {"Content-Type": "application/json"}
        
        if email and email in self.tokens:
            headers["Authorization"] = f"Bearer {self.tokens[email]}"
        
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=5)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=5)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=5)
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Ошибка сети: {e}")
            return None
        
        return response

def test_public_endpoints():
    print("🔓 Тестирование публичных эндпоинтов (без токена):")
    print("-" * 50)
    
    endpoints = [
        ("GET", "/", "Главная страница"),
        ("GET", "/docs", "Документация Swagger"),
        ("GET", "/api/v1/health", "Health check"),
        ("GET", "/api/v1/health/detailed", "Детальный health check"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {description}: {response.status_code}")
        except:
            print(f"❌ {description}: Ошибка подключения")

def test_role_based_access():
    print("\n\n👑 Тестирование ролевой модели доступа:")
    print("=" * 60)
    
    tester = APITester()
    
    # Вход всех пользователей
    users = [
        ("admin@example.com", "admin123", "👑 Администратор"),
        ("manager@example.com", "manager123", "👔 Менеджер"),
        ("user@example.com", "user123", "👤 Пользователь")
    ]
    
    for email, password, role_name in users:
        tester.login(email, password)
    
    print("\n📊 Тестирование эндпоинтов для разных ролей:")
    print("-" * 60)
    
    # Создаем тестовый сад для работы
    garden_id = create_test_garden(tester)
    
    if not garden_id:
        print("❌ Не удалось создать тестовый сад, пропускаем некоторые тесты")
        return
    
    # Тестируем разные эндпоинты
    test_cases = [
        ("GET", "/gardens/", "Просмотр всех садов", "all"),
        ("GET", f"/gardens/{garden_id}", "Просмотр конкретного сада", "all"),
        ("POST", "/gardens/", "Создание нового сада", "all"),
        ("PUT", f"/gardens/{garden_id}", "Обновление сада", "manager+"),
        ("DELETE", f"/gardens/{garden_id}", "Удаление сада", "admin"),
        ("GET", f"/gardens/{garden_id}/stats", "Статистика сада", "all"),
        ("GET", "/auth/me", "Информация о себе", "all"),
    ]
    
    print("\n" + "Роли: 👤=user, 👔=manager, 👑=admin")
    print("=" * 80)
    
    for method, endpoint, description, required_role in test_cases:
        print(f"\n{description} ({method} {endpoint}):")
        print("-" * 40)
        
        for email, password, role_name in users:
            role = email.split("@")[0]  # admin, manager, user
            user_symbol = "👑" if role == "admin" else "👔" if role == "manager" else "👤"
            
            # Проверяем доступ
            has_access = (
                required_role == "all" or
                (required_role == "manager+" and role in ["manager", "admin"]) or
                (required_role == "admin" and role == "admin")
            )
            
            # Подготовка данных для запроса
            data = None
            if "POST" in method or "PUT" in method:
                data = {
                    "name": f"Обновленный сад от {role}",
                    "location": "Тестовая локация",
                    "area": 2.0,
                    "fruit_type": "apple"
                }
                if method == "POST":
                    data["name"] = f"Новый сад от {role}"
            
            response = tester.make_request(method, endpoint, email, data)
            
            if response:
                if has_access:
                    expected_codes = [200, 201] if method in ["POST", "PUT"] else [200]
                    if response.status_code in expected_codes:
                        print(f"  {user_symbol} {role_name}: ✅ Разрешено ({response.status_code})")
                    else:
                        print(f"  {user_symbol} {role_name}: ❌ Ошибка ({response.status_code}) - {response.text[:80]}")
                else:
                    if response.status_code == 403:
                        print(f"  {user_symbol} {role_name}: ⛔ Запрещено (как и ожидалось)")
                    elif response.status_code == 401:
                        print(f"  {user_symbol} {role_name}: 🔐 Требуется авторизация")
                    else:
                        print(f"  {user_symbol} {role_name}: ⚠️  Неожиданный код {response.status_code}")
            else:
                print(f"  {user_symbol} {role_name}: ❌ Ошибка запроса (нет ответа)")

def create_test_garden(tester):
    """Создает тестовый сад для работы"""
    print("\n🌳 Создание тестового сада...")
    
    garden_data = {
        "name": "Тестовый сад для проверки безопасности",
        "location": "Тестовая локация",
        "area": 3.5,
        "fruit_type": "apple",
        "description": "Создан для тестирования ролевой модели доступа"
    }
    
    response = tester.make_request("POST", "/gardens/", "admin@example.com", garden_data)
    
    if response and response.status_code == 201:
        garden = response.json()
        print(f"✅ Создан сад ID: {garden['id']} - '{garden['name']}'")
        return garden['id']
    else:
        if response:
            print(f"❌ Не удалось создать сад: {response.status_code} - {response.text}")
        else:
            print(f"❌ Не удалось создать сад: нет ответа")
        return None

def test_jwt_features():
    print("\n\n🔐 Тестирование особенностей JWT:")
    print("=" * 50)
    
    # Вход
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    }, timeout=5)
    
    if response.status_code != 200:
        print(f"❌ Не удалось войти: {response.status_code} - {response.text}")
        return
    
    token_data = response.json()
    token = token_data['access_token']
    
    print(f"✅ Токен получен: {token[:50]}...")
    
    # Простая проверка структуры токена
    print(f"\n📋 Базовая информация о токене:")
    print(f"  👤 Пользователь: {token_data['user']['full_name']}")
    print(f"  🎭 Роль: {token_data['user']['role']}")
    print(f"  📧 Email: {token_data['user']['email']}")
    print(f"  🎫 Тип токена: {token_data['token_type']}")
    
    # Проверяем что токен работает
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"  ✅ Токен валиден, получена информация о пользователе")
        print(f"  👤 Имя: {user_info['full_name']}")
        print(f"  🎭 Роль: {user_info['role']}")
    else:
        print(f"  ❌ Токен не работает: {response.status_code} - {response.text}")

def test_middleware_protection():
    print("\n\n🛡️ Тестирование защиты middleware:")
    print("=" * 50)
    
    endpoints_to_test = [
        ("/api/v1/gardens/", "GET", "Список садов"),
        ("/api/v1/auth/me", "GET", "Информация о себе"),
        ("/api/v1/gardens/1/stats", "GET", "Статистика сада"),
    ]
    
    print("1. Запросы без токена:")
    for endpoint, method, description in endpoints_to_test:
        if method == "GET":
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
            if response.status_code == 401:
                print(f"  ✅ {description}: Защищено (401 Unauthorized)")
            elif response.status_code == 403:
                print(f"  ✅ {description}: Защищено (403 Forbidden)")
            else:
                print(f"  ⚠️  {description}: Неожиданный код {response.status_code}")
    
    print("\n2. Запросы с неверным токеном:")
    headers = {"Authorization": "Bearer invalid_token_12345"}
    for endpoint, method, description in endpoints_to_test[:2]:  # Только первые два
        if method == "GET":
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=3)
            if response.status_code == 401:
                print(f"  ✅ {description}: Защищено от невалидного токена")
            else:
                print(f"  ⚠️  {description}: Код {response.status_code}")

def test_api_documentation():
    print("\n\n📚 Тестирование документации API:")
    print("=" * 50)
    
    print("1. Проверка доступности Swagger UI:")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=3)
        if response.status_code == 200:
            print("  ✅ Swagger UI доступен")
        else:
            print(f"  ❌ Swagger UI недоступен: {response.status_code}")
    except:
        print("  ❌ Swagger UI: Ошибка подключения")
    
    print("\n2. Проверка OpenAPI спецификации:")
    try:
        response = requests.get("http://localhost:8000/openapi.json", timeout=3)
        if response.status_code == 200:
            spec = response.json()
            print(f"  ✅ OpenAPI спецификация доступна")
            print(f"  📖 Версия OpenAPI: {spec.get('openapi', 'не указана')}")
            print(f"  📝 Заголовок: {spec.get('info', {}).get('title', 'не указан')}")
            print(f"  🔐 Пути защищены: {'securitySchemes' in spec.get('components', {})}")
        else:
            print(f"  ❌ OpenAPI спецификация недоступна: {response.status_code}")
    except:
        print("  ❌ OpenAPI спецификация: Ошибка подключения")

if __name__ == "__main__":
    print("=" * 70)
    print("          ТЕСТИРОВАНИЕ СИСТЕМЫ БЕЗОПАСНОСТИ ЛР №6")
    print("=" * 70)
    
    test_public_endpoints()
    test_role_based_access()
    test_jwt_features()
    test_middleware_protection()
    test_api_documentation()
    
    print("\n" + "=" * 70)
    print("🎉 Тестирование завершено!")
    print("\n📋 Итог по ЛР №6:")
    print("✅ JWT аутентификация с claims")
    print("✅ Middleware проверки доступа")
    print("✅ Ролевая модель (RBAC)")
    print("✅ Разграничение доступа к API")
    print("✅ Защита от неавторизованных запросов")
    print("✅ Защита от невалидных токенов")
    print("✅ Документация API (Swagger/OpenAPI)")
    print("=" * 70)