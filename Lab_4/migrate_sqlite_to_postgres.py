# migrate_sqlite_to_postgres.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Figure, Part, User, UserFigure

# Шлях до старої бази
SQLITE_URL = "sqlite:///figurines.db"
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_db = SQLiteSession()

# Підключення до PostgreSQL
POSTGRES_URL = "postgresql+psycopg2://postgres:2684@localhost:5432/dragoncollect"
postgres_engine = create_engine(POSTGRES_URL)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_db = PostgresSession()

# Переносимо таблиці
Base.metadata.create_all(bind=postgres_engine)

# ==== Перенос Part ====
for part in sqlite_db.query(Part).all():
    new_part = Part(id=part.id, title=part.title)
    postgres_db.add(new_part)

# ==== Перенос Figure ====
for fig in sqlite_db.query(Figure).all():
    new_fig = Figure(
        id=fig.id,
        name=fig.name,
        img_url=fig.img_url,
        hover_img_url=fig.hover_img_url,
        owned=fig.owned,
        part_id=fig.part_id
    )
    postgres_db.add(new_fig)

# ==== Перенос User ====
for user in sqlite_db.query(User).all():
    new_user = User(
        id=user.id,
        username=user.username,
        password=user.password,
        is_admin=user.is_admin
    )
    postgres_db.add(new_user)

# ==== Перенос UserFigure ====
for uf in sqlite_db.query(UserFigure).all():
    new_uf = UserFigure(
        id=uf.id,
        user_id=uf.user_id,
        figure_id=uf.figure_id,
        owned=uf.owned
    )
    postgres_db.add(new_uf)

# Підтверджуємо вставку
postgres_db.commit()

print("✅ Дані перенесено з SQLite у PostgreSQL")
