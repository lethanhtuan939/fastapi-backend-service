from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from typing import List


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(u_username=user.username, u_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, offset: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(offset).limit(limit).all()


def get_user(db: Session, user_id: str) -> User:
    return db.query(User).filter(User.u_id == user_id).first()
