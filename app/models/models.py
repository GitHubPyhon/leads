from sqlalchemy import Date, Column, ForeignKey, Integer, String
from sqlalchemy.sql.functions import now

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    created_at = Column(Date, server_default=now())
    email = Column(String, unique=True)
    full_name = Column(String)
    country = Column(String)
