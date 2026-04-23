def test_create_garden_as_user(client, auth_headers, test_user):
    # user не имеет прав на создание
    response = client.post("/api/v1/gardens/", json={
        "name": "New Garden",
        "location": "Test Location",
        "area": 2.5,
        "fruit_type": "apple"
    }, headers=auth_headers)
    assert response.status_code == 403

def test_create_garden_as_admin(client, admin_user, db_session):
    # сначала логинимся как админ
    login = client.post("/api/v1/auth/login", json={
        "email": admin_user.email,
        "password": "admin123"
    }).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    response = client.post("/api/v1/gardens/", json={
        "name": "Admin Garden",
        "location": "Admin Location",
        "area": 10.0,
        "fruit_type": "apple"
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Admin Garden"