import requests
import json

BASE_URL = "http://localhost:8000/api/v1/gardens"

def test_crud_operations():
    print("🧪 Тестирование CRUD операций для садов...")
    
    # 1. GET - Получить все сады
    print("\n1. GET /gardens/")
    response = requests.get(BASE_URL + "/")
    print(f"   Status: {response.status_code}")
    print(f"   Gardens: {len(response.json())}")
    
    # 2. POST - Создать новый сад
    print("\n2. POST /gardens/")
    new_garden = {
        "name": "Вишневый сад Западный",
        "location": "Тульская область, Щёкинский район", 
        "area": 0.8,
        "fruit_type": "cherry"
    }
    response = requests.post(BASE_URL + "/", json=new_garden)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        created_garden = response.json()
        print(f"   Created: {created_garden['name']} (ID: {created_garden['id']})")
        garden_id = created_garden['id']
    else:
        print(f"   Error: {response.text}")
        return
    
    # 3. GET - Получить конкретный сад
    print(f"\n3. GET /gardens/{garden_id}")
    response = requests.get(BASE_URL + f"/{garden_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Garden: {response.json()['name']}")
    
    # 4. PUT - Обновить сад
    print(f"\n4. PUT /gardens/{garden_id}")
    update_data = {
        "name": "Вишневый сад Обновленный",
        "area": 1.0
    }
    response = requests.put(BASE_URL + f"/{garden_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Updated: {response.json()['name']}")
    
    # 5. GET - Получить статистику
    print(f"\n5. GET /gardens/{garden_id}/stats")
    response = requests.get(BASE_URL + f"/{garden_id}/stats")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"   Stats: {stats['total_trees']} trees, {stats['health_score']}% health")
    
    # 6. DELETE - Удалить сад
    print(f"\n6. DELETE /gardens/{garden_id}")
    response = requests.delete(BASE_URL + f"/{garden_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Deleted: {response.json()['message']}")
    
    # 7. Проверка ошибок
    print("\n7. Тестирование обработки ошибок...")
    
    # Несуществующий сад
    response = requests.get(BASE_URL + "/999")
    print(f"   GET non-existent: {response.status_code} - {response.json()['detail']}")
    
    # Дубликат имени
    duplicate_garden = {
        "name": "Яблоневый сад Северный",  # Дубликат
        "location": "Другое место",
        "area": 1.0,
        "fruit_type": "apple"
    }
    response = requests.post(BASE_URL + "/", json=duplicate_garden)
    print(f"   POST duplicate: {response.status_code} - {response.json()['detail']}")

if __name__ == "__main__":
    test_crud_operations()