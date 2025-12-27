from sqlalchemy import Column, String
from app.models.base import Base


from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    u_id = Column(String, primary_key=True, index=True)
    u_username = Column(String, unique=True, index=True)
    u_password = Column(String)

    tokens = relationship("Token", back_populates="user")