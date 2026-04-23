import pytest
from app.models.database import Garden
@pytest.fixture
def test_manager(manager_user):
    return manager_user

@pytest.fixture
def test_admin(admin_user):
    return admin_user

@pytest.fixture
def db(db_session):
    return db_session

def test_register_user(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "newpass123",
        "full_name": "New User",
        "role": "user"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email

def test_login_invalid_password(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "wrong"
    })
    assert response.status_code == 401

def test_refresh_token(client, test_user):
    # Сначала логинимся
    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    refresh = login_resp.json()["refresh_token"]
    # Обновляем
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh

def test_logout(client, test_user):
    login = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    refresh = login.json()["refresh_token"]
    access = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {access}"}
    resp = client.post("/api/v1/auth/logout", json={"refresh_token": refresh}, headers=headers)
    assert resp.status_code == 200
    # Повторное использование refresh токена должно дать 401
    resp2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert resp2.status_code == 401

def test_create_garden_as_user(client, auth_headers):
    resp = client.post("/api/v1/gardens/", headers=auth_headers, json={
        "name": "User Garden",
        "location": "Test Location",
        "area": 2.5,
        "fruit_type": "apple"
    })
    assert resp.status_code == 403  # только менеджер и выше

def test_create_garden_as_manager(client, test_manager):
    # Логин менеджера
    login = client.post("/api/v1/auth/login", json={
        "email": test_manager.email,
        "password": "manager123"
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resp = client.post("/api/v1/gardens/", headers=headers, json={
        "name": "Manager Garden",
        "location": "North Field",
        "area": 3.0,
        "fruit_type": "pear"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Manager Garden"

def test_delete_garden_as_manager(client, test_manager, db):
    # Создадим сад
    garden = Garden(name="ToDelete", location="Any", area=1, fruit_type="apple")
    db.add(garden)
    db.commit()
    db.refresh(garden)
    login = client.post("/api/v1/auth/login", json={
        "email": test_manager.email,
        "password": "manager123"
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resp = client.delete(f"/api/v1/gardens/{garden.id}", headers=headers)
    assert resp.status_code == 403  # только админ

def test_delete_garden_as_admin(client, test_admin, db):
    garden = Garden(name="AdminDelete", location="Any", area=1, fruit_type="apple")
    db.add(garden)
    db.commit()
    db.refresh(garden)
    login = client.post("/api/v1/auth/login", json={
        "email": test_admin.email,
        "password": "admin123"
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resp = client.delete(f"/api/v1/gardens/{garden.id}", headers=headers)
    assert resp.status_code == 200

def test_filter_gardens(client, test_manager, db):
    # Создаём тестовые сады
    db.query(Garden).delete()
    db.add_all([
        Garden(name="Apple Garden", location="North", area=2, fruit_type="apple"),
        Garden(name="Pear Garden", location="South", area=3, fruit_type="pear")
    ])
    db.commit()
    login = client.post("/api/v1/auth/login", json={
        "email": test_manager.email,
        "password": "manager123"
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resp = client.get("/api/v1/gardens/?fruit_type=apple", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Apple Garden"