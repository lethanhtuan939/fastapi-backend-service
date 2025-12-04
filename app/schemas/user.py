from app.schemas.base import BaseSchema
from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseSchema):
    u_id: Optional[str] = None
    u_username: str

    class Config:
        from_attributes = True  # For serialize from SQLAlchemy model
