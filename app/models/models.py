from sqlalchemy import Date, Column, ForeignKey, Integer, String
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created_at = Column(Date)
    email = Column(String)
    full_name = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    tasks = relationship("Task", back_populates="users")
    countries = relationship(
        "Country",
        back_populates="users",
        cascade="save-update, merge, delete"
    )


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    created_at = Column(Date)
    country_id = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    users = relationship("User", back_populates="countries")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    created_at = Column(Date, server_default=now())
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="CREATED")
    users = relationship(
        "User",
        back_populates="tasks",
        cascade="save-update, merge, delete"
    )
