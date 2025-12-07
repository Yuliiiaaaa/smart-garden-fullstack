from sqlalchemy.orm import Session
from app.models.database import User, SessionLocal
from app.core.security import get_password_hash

def create_test_user():
    """Создает тестового пользователя для разработки"""
    db = SessionLocal()
    
    # Проверяем, существует ли уже тестовый пользователь
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    
    if not existing_user:
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("test123"),
            full_name="Тестовый Пользователь",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print("✅ Создан тестовый пользователь:")
        print("   Email: test@example.com")
        print("   Пароль: test123")
    else:
        print("✅ Тестовый пользователь уже существует")
    
    db.close()

if __name__ == "__main__":
    create_test_user()