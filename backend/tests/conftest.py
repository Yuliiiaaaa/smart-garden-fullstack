import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import Base, get_db, User
from app.core.security import get_password_hash

# Создаём engine ОДИН РАЗ
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Создаём таблицы ПРЯМО СЕЙЧАС (до фикстур)
Base.metadata.create_all(bind=engine)

# Фабрика сессий
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Создаёт новую сессию и откатывает изменения после теста"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Создаёт клиент с переопределённой сессией БД"""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# ========== НОВЫЕ ФИКСТУРЫ ==========

@pytest.fixture
def test_user(db_session):
    """Создаёт тестового пользователя с ролью user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        role="user",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session):
    """Создаёт тестового администратора"""
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def manager_user(db_session):
    """Создаёт тестового менеджера"""
    user = User(
        email="manager@test.com",
        hashed_password=get_password_hash("manager123"),
        full_name="Manager User",
        role="manager",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Возвращает заголовки авторизации для тестового пользователя"""
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Возвращает заголовки авторизации для администратора"""
    response = client.post("/api/v1/auth/login", json={
        "email": admin_user.email,
        "password": "admin123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def manager_auth_headers(client, manager_user):
    """Возвращает заголовки авторизации для менеджера"""
    response = client.post("/api/v1/auth/login", json={
        "email": manager_user.email,
        "password": "manager123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Моки для внешних сервисов
@pytest.fixture
def mock_s3(mocker):
    """Мок для S3 хранилища"""
    mock = mocker.patch("app.core.storage.StorageService.upload_file")
    mock.return_value = "mock-key"
    return mock

@pytest.fixture
def mock_weather(mocker):
    """Мок для погодного сервиса"""
    mock = mocker.patch("app.services.weather_service.WeatherService.get_weather")
    mock.return_value = {
        "temperature": 18.5,
        "feels_like": 17.2,
        "humidity": 65,
        "description": "облачно",
        "icon": "04d",
        "wind_speed": 3.2
    }
    return mock


# Пропуск проблемных тестов
import pytest



# Переопределяем фикстуры для интеграционных тестов
@pytest.fixture
def test_manager(manager_user):
    return manager_user

@pytest.fixture
def test_admin(admin_user):
    return admin_user

@pytest.fixture
def db(db_session):
    return db_session