from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from typing import List, Dict, Any
from app.repositories.user_repository import UserRepository
import uuid
from sqlalchemy import desc

user_repo = UserRepository()


def create_user(db: Session, user_create: UserCreate) -> User:
    user_data = {
        User.u_id.name: str(uuid.uuid4()),
        User.u_username.name: user_create.username,
        User.u_password.name: hash_password(user_create.password),
        User.created_by.name: "SYS",
        User.updated_by.name: "SYS",
    }

    return user_repo.create(db, user_data)


def get_users(db: Session, offset: int = 0, limit: int = 10) -> List[User]:
    return user_repo.find_all(db, offset=offset, limit=limit)


def get_user(db: Session, user_id: str) -> User:
    condition = {"u_id": user_id}
    return user_repo.find_one_by_conditions(db, **condition)


def get_users_paginated(
    db: Session,
    page_no: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    result = user_repo.paginate(
        db=db,
        page=page_no,
        per_page=page_size,
        # order_by=desc(User.created_at),
    )

    return {
        "items": result["items"],
        "total": result["total"],
        "page_no": page_no,
        "page_size": page_size,
        "total_pages": result["pages"],
        "has_next": page_no < result["pages"],
        "has_prev": page_no > 1,
    }
