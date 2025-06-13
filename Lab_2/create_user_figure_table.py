# create_user_figures_table.py
# Окремий запуск для створення таблиці user_figures, якщо вона ще не існує

from database import engine
from models import UserFigure, Base

# Створює таблицю user_figures у базі даних, якщо вона ще не створена
UserFigure.__table__.create(bind=engine, checkfirst=True)
print("Таблиця user_figures створена")
