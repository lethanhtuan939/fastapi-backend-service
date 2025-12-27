from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.enum import TokenType
from app.models.base import Base


class Token(Base):
    __tablename__ = "tbl_token"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    token_type = Column(Enum(TokenType))
    expired = Column(Boolean, default=False)
    revoked = Column(Boolean, default=False)
    user_id = Column(String, ForeignKey("users.u_id"))

    user = relationship("User", back_populates="tokens")
