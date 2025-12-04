from sqlalchemy import Column, String
from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    u_id = Column(String, primary_key=True, index=True)
    u_username = Column(String, unique=True, index=True)
    u_password = Column(String)
