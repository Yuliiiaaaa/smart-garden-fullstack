from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from sqlalchemy import Boolean, String
import secrets

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