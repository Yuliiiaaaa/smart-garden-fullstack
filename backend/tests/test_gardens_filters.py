def test_garden_filters(client, auth_headers, db_session):
    # Создаём несколько садов
    # ... (создание через админа)
    response = client.get("/api/v1/gardens/?fruit_type=apple&sort_by=area&sort_order=desc&skip=0&limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)