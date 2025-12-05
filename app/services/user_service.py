from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from typing import List
from app.repositories.user_repository import UserRepository

user_repo = UserRepository()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(u_username=user.username, u_password=hash_password(user.password))
    return user_repo.create(db, db_user)


def get_users(db: Session, offset: int = 0, limit: int = 10) -> List[User]:
    return user_repo.find_all(db, offset=offset, limit=limit)


def get_user(db: Session, user_id: str) -> User:
    condition = {"u_id": user_id}
    return user_repo.find_one_by_conditions(db, **condition)
