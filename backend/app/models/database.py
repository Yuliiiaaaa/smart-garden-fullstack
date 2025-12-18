# app/models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Создаем базовый класс для моделей
Base = declarative_base()

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

    # Связи
    harvest_records = relationship("HarvestRecord", back_populates="user", cascade="all, delete-orphan")

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
    """Модель записи урожая (ОБНОВЛЕННАЯ ВЕРСИЯ)"""
    __tablename__ = "harvest_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, nullable=True)  # Может быть NULL
    garden_id = Column(Integer, nullable=True)  # Добавляем garden_id
    fruit_count = Column(Integer, nullable=False)
    fruit_type = Column(String(50), nullable=True, default='apple')  # Добавляем fruit_type
    image_path = Column(String(500), nullable=True)
    confidence_score = Column(Float, default=0.0)
    processing_time = Column(Float, nullable=True)  # Добавляем processing_time
    harvest_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Добавляем user_id с ForeignKey
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    user = relationship("User", back_populates="harvest_records")

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
            print(f" Создан пользователь: {user_data['email']} ({user_data['role']})")
        
        db.commit()
        print(" Тестовые пользователи успешно созданы!")
        
    except Exception as e:
        print(f"  Ошибка при создании тестовых пользователей: {e}")
        db.rollback()
    finally:
        db.close()

# app/models/database.py
# В конец файла добавьте функцию create_test_data:

def create_test_data():
    """Создает тестовые данные: сады, деревья"""
    db = SessionLocal()
    try:
        # Очищаем старые тестовые данные (опционально)
        db.query(Tree).delete()
        db.query(Garden).delete()
        db.commit()
        
        # Создаем тестовые сады
        test_gardens = [
            {
                "name": "Яблоневый сад 'Северный'",
                "location": "Северный участок, ряд 1-10",
                "area": 2.5,
                "fruit_type": "apple",
                "description": "Сад с яблонями сортов Голден и Фуджи"
            },
            {
                "name": "Грушевый сад 'Южный'", 
                "location": "Южный участок, ряд 1-5",
                "area": 1.8,
                "fruit_type": "pear",
                "description": "Сад с грушами сортов Конференция и Вильямс"
            },
            {
                "name": "Вишневый сад 'Восточный'",
                "location": "Восточный участок, ряд 1-3",
                "area": 0.8,
                "fruit_type": "cherry",
                "description": "Сад с вишней сорта Шпанка"
            },
            {
                "name": "Смешанный сад 'Центральный'",
                "location": "Центральный участок",
                "area": 3.2,
                "fruit_type": "apple",
                "description": "Смешанный сад с яблонями и грушами"
            }
        ]
        
        created_gardens = []
        for garden_data in test_gardens:
            new_garden = Garden(
                name=garden_data["name"],
                location=garden_data["location"],
                area=garden_data["area"],
                fruit_type=garden_data["fruit_type"],
                description=garden_data["description"]
            )
            db.add(new_garden)
            created_gardens.append(new_garden)
        
        db.commit()
        
        # Обновляем объекты с ID
        for garden in created_gardens:
            db.refresh(garden)
        
        print(" Созданы тестовые сады:")
        for garden in created_gardens:
            print(f"   - {garden.name} ({garden.fruit_type}, {garden.area} га)")
        
        # Создаем тестовые деревья для каждого сада
        fruit_varieties = {
            "apple": ["Голден", "Фуджи", "Гала", "Ред Делишес", "Айдаред"],
            "pear": ["Конференция", "Вильямс", "Дюшес", "Бере Боск"],
            "cherry": ["Шпанка", "Владимирская", "Любская", "Чернокорка"]
        }
        
        tree_counter = 1
        for garden in created_gardens:
            # Количество деревьев зависит от площади сада
            trees_count = int(garden.area * 60)  # Примерно 60 деревьев на гектар
            
            for row in range(1, 6):  # 5 рядов
                trees_in_row = trees_count // 5
                for tree_num in range(1, trees_in_row + 1):
                    # Выбираем случайный сорт для данного типа фруктов
                    varieties = fruit_varieties.get(garden.fruit_type, ["Неизвестный"])
                    variety = varieties[tree_counter % len(varieties)]
                    
                    new_tree = Tree(
                        garden_id=garden.id,
                        row_number=row,
                        tree_number=tree_num,
                        variety=variety,
                        planting_year=2018 + (tree_counter % 5)  # Год посадки от 2018 до 2022
                    )
                    db.add(new_tree)
                    tree_counter += 1
        
        db.commit()
        print(f" Создано {tree_counter - 1} тестовых деревьев")
        
        # Создаем тестовые записи урожая
        import random
        from datetime import datetime, timedelta
        
        # Получаем всех пользователей
        users = db.query(User).all()
        
        for user in users:
            for _ in range(5):  # По 5 записей на каждого пользователя
                # Выбираем случайный сад
                garden = random.choice(created_gardens)
                
                # Случайная дата за последний месяц
                days_ago = random.randint(1, 30)
                harvest_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # Случайное количество плодов
                fruit_count = random.randint(5, 45)
                
                new_record = HarvestRecord(
                    garden_id=garden.id,
                    fruit_count=fruit_count,
                    fruit_type=garden.fruit_type,
                    confidence_score=random.uniform(0.7, 0.97),
                    processing_time=random.uniform(1.5, 4.2),
                    user_id=user.id,
                    harvest_date=harvest_date
                )
                db.add(new_record)
        
        db.commit()
        print(" Созданы тестовые записи урожая")
        
        print(" Все тестовые данные успешно созданы!")
        
    except Exception as e:
        print(f" Ошибка при создании тестовых данных: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


# Обновляем вызов
create_test_users()