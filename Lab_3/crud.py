# crud.py
# Операції доступу до бази даних для фігурок, частин і користувачів

from sqlalchemy.orm import Session
from models import Figure, Part
from models import User

# Повертає всі фігурки з бази даних
def get_all_figures(db: Session):
    return db.query(Figure).all()

# Повертає всі частини з бази даних
def get_parts(db: Session):
    return db.query(Part).all()

# Створює нову фігурку у базі даних
def create_figure(db: Session, figure_data):
    figure = Figure(**figure_data)
    db.add(figure)
    db.commit()
    db.refresh(figure)
    return figure

# Створює нового користувача у базі даних
def create_user(db: Session, username: str, password: str, is_admin: bool = False):
    user = User(username=username, password=password, is_admin=is_admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user