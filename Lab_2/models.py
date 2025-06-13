# models.py
# Містить визначення ORM-моделей для бази даних: частини, фігурки, користувачі та зв’язок між користувачами й фігурками


from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


# Таблиця частин (категорій) для фігурок
class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)

    figures = relationship("Figure", back_populates="part")


# Таблиця фігурок з посиланням на частину
class Figure(Base):
    __tablename__ = "figures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    img_url = Column(String)
    hover_img_url = Column(String)
    owned = Column(Boolean, default=False)

    part_id = Column(Integer, ForeignKey("parts.id"))
    part = relationship("Part", back_populates="figures")


# Таблиця користувачів із розмежуванням ролей
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  
    is_admin = Column(Boolean, default=False)


# Таблиця зв’язків фігурок і користувачів з прапором володіння
class UserFigure(Base):
    __tablename__ = "user_figures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    figure_id = Column(Integer, ForeignKey("figures.id"))
    owned = Column(Boolean, default=False)

    user = relationship("User", back_populates="figures")
    figure = relationship("Figure", back_populates="users")

    __table_args__ = (UniqueConstraint('user_id', 'figure_id', name='_user_figure_uc'),)

# Двосторонній зв’язок між User і UserFigure
User.figures = relationship("UserFigure", back_populates="user")
# Двосторонній зв’язок між Figure і UserFigure
Figure.users = relationship("UserFigure", back_populates="figure")
