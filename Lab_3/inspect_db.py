# inspect_db.py
# Допоміжний скрипт для виводу списку таблиць у базі даних SQLite

from sqlalchemy import create_engine, inspect

engine = create_engine("sqlite:///figurines.db") 
inspector = inspect(engine)

tables = inspector.get_table_names()
print("Таблиці в базі даних:")
for table in tables:
    print("-", table)
