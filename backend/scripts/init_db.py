# scripts/init_db.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import create_test_users, create_test_data, engine, Base

if __name__ == "__main__":
    print("🔄 Инициализация базы данных...")
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
    
    # Создаем тестовых пользователей
    create_test_users()
    
    # Создаем тестовые данные
    create_test_data()
    
    print(" База данных успешно инициализирована!")