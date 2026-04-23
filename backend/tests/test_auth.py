def test_register_success(client, db_session):
    response = client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "newpass123",
        "full_name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "user"

def test_register_duplicate_email(client, test_user):
    response = client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "password": "password123",  
        "full_name": "Duplicate"
    })
    assert response.status_code == 400

def test_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_user.email

def test_login_wrong_password(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "wrong"
    })
    assert response.status_code == 401

def test_refresh_token(client, test_user):
    login = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    }).json()
    refresh = login["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert new_tokens["refresh_token"] != refresh

def test_logout(client, test_user):
    login = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    }).json()
    refresh = login["refresh_token"]
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh}, headers=headers)
    assert response.status_code == 200