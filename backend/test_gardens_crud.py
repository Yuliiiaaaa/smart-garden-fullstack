import sqlite3
import os

def check_database():
    db_path = "./smart_garden.db"
    
    if not os.path.exists(db_path):
        print(" Файл базы данных не найден!")
        return
    
    print(" Проверка базы данных...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f" Таблицы в БД: {[table[0] for table in tables]}")
        
        # Проверяем данные в таблице gardens
        cursor.execute("SELECT COUNT(*) FROM gardens;")
        garden_count = cursor.fetchone()[0]
        print(f" Садов в базе: {garden_count}")
        
        if garden_count > 0:
            cursor.execute("SELECT id, name, location, area FROM gardens;")
            gardens = cursor.fetchall()
            print(" Список садов:")
            for garden in gardens:
                print(f"   ID: {garden[0]}, Название: {garden[1]}, Место: {garden[2]}, Площадь: {garden[3]} га")
        
        # Проверяем данные в таблице trees
        cursor.execute("SELECT COUNT(*) FROM trees;")
        tree_count = cursor.fetchone()[0]
        print(f" Деревьев в базе: {tree_count}")
        
        conn.close()
        print(" База данных работает корректно!")
        
    except Exception as e:
        print(f" Ошибка при проверке БД: {e}")

if __name__ == "__main__":
    check_database()