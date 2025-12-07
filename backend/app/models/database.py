from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from sqlalchemy import Boolean, String
import secrets
from sqlalchemy import Enum as SQLEnum

# Создаем базовый класс для моделей
Base = declarative_base()

class Garden(Base):
    """Модель сада"""
    __tablename__ = "gardens"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    area = Column(Float, nullable=False)  # площадь в гектарах
    fruit_type = Column(String(50), nullable=False)  # яблоки, груши и т.д.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Tree(Base):
    """Модель дерева"""
    __tablename__ = "trees"
    
    id = Column(Integer, primary_key=True, index=True)
    garden_id = Column(Integer, nullable=False)
    row_number = Column(Integer, nullable=False)
    tree_number = Column(Integer, nullable=False)
    variety = Column(String(50), nullable=False)  # сорт
    planting_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HarvestRecord(Base):
    """Модель записи урожая"""
    __tablename__ = "harvest_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, nullable=False)
    harvest_date = Column(DateTime, default=datetime.utcnow)
    fruit_count = Column(Integer, nullable=False)
    image_path = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)  # точность ИИ анализа

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # admin, manager, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)



# Настройка подключения к БД
DATABASE_URL = "sqlite:///./smart_garden.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Создаем сессию для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_test_users():
    """Создает тестовых пользователей с разными ролями"""
    db = SessionLocal()
    try:
        from app.core.security import get_password_hash
        
        # Удаляем старых тестовых пользователей (опционально)
        db.query(User).filter(User.email.in_([
            "admin@example.com",
            "manager@example.com", 
            "user@example.com",
            "test@example.com"
        ])).delete(synchronize_session=False)
        
        # Список тестовых пользователей с разными ролями
        test_users = [
            {
                "email": "admin@example.com",
                "full_name": "Администратор Системы", 
                "password": "admin123",
                "role": "admin"
            },
            {
                "email": "manager@example.com",
                "full_name": "Менеджер Садов",
                "password": "manager123",
                "role": "manager"
            },
            {
                "email": "user@example.com",
                "full_name": "Обычный Пользователь",
                "password": "user123",
                "role": "user"
            }
        ]
        
        for user_data in test_users:
            hashed_password = get_password_hash(user_data["password"])
            new_user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                role=user_data["role"]
            )
            db.add(new_user)
            print(f"✅ Создан пользователь: {user_data['email']} ({user_data['role']})")
        
        db.commit()
        print("🎉 Тестовые пользователи успешно созданы!")
        
    except Exception as e:
        print(f"⚠️  Ошибка при создании тестовых пользователей: {e}")
        db.rollback()
    finally:
        db.close()

# Обновляем вызов
create_test_users()
