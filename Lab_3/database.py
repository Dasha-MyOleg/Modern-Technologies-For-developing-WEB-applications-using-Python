# database.py
# Підключення до бази даних SQLite та налаштування SQLAlchemy ORM

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL бази даних SQLite
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:2684@localhost:5432/dragoncollect"

# Створення рушія бази даних
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Створення сесії для взаємодії з базою даних
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас для моделей SQLAlchemy
Base = declarative_base()
