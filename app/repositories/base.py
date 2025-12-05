from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, insert, func
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from loguru import logger
import math

T = TypeVar("T")

RETRY_CONFIG = dict(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(SQLAlchemyError),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"DB retry {retry_state.attempt_number}/3 | error: {retry_state.outcome.exception()}"
    ),
)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    @retry(**RETRY_CONFIG)
    def _execute(self, db: Session, stmt):
        try:
            result = db.execute(stmt)
            db.flush()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Database error in {self.model.__name__}: {e}")
            raise

    # ====================== CREATE ======================
    def create(self, db: Session, data: Dict[str, Any]) -> T:
        stmt = insert(self.model).values(**data).returning(self.model)
        result = self._execute(db, stmt)
        return result.scalar_one()

    def bulk_create(self, db: Session, data: List[Dict[str, Any]]) -> None:
        if not data:
            return
        stmt = insert(self.model).values(data)
        self._execute(db, stmt)

    # ====================== READ ======================
    def find_one_by_conditions(self, db: Session, **conditions) -> Optional[T]:
        stmt = select(self.model).filter_by(**conditions).limit(1)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def find_by_conditions(self, db: Session, **conditions) -> List[T]:
        stmt = select(self.model).filter_by(**conditions)
        result = db.execute(stmt)
        return list(result.scalars().all())

    def find_by_field(self, db: Session, **conditions) -> Optional[T]:
        stmt = select(self.model).filter_by(**conditions).limit(1)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def find_all(
        self,
        db: Session,
        conditions: Optional[Dict[str, Any]] = None,
        order_by=None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[T]:
        stmt = select(self.model)
        if conditions:
            stmt = stmt.filter_by(**conditions)
        if order_by:
            stmt = stmt.order_by(order_by)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = db.execute(stmt)
        return list(result.scalars().all())

    def count(self, db: Session, conditions: Optional[Dict[str, Any]] = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if conditions:
            stmt = stmt.filter_by(**conditions)
        result = db.execute(stmt)
        return result.scalar_one()

    def paginate(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 20,
        conditions: Optional[Dict[str, Any]] = None,
        order_by=None,
    ) -> Dict[str, Any]:
        total = self.count(db, conditions)
        items = self.find_all(
            db,
            conditions=conditions,
            order_by=order_by,
            offset=(page - 1) * per_page,
            limit=per_page,
        )

        total_pages = math.ceil(total / per_page) if total > 0 else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    # ====================== UPDATE ======================
    def update(self, db: Session, instance: T, data: Dict[str, Any]) -> T:
        for key, value in data.items():
            setattr(instance, key, value)
        db.flush()
        return instance

    def update_by_id(
        self, db: Session, id_value: Any, data: Dict[str, Any]
    ) -> Optional[T]:
        stmt = (
            update(self.model)
            .where(self.model.id == id_value)
            .values(**data)
            .returning(self.model)
        )
        result = self._execute(db, stmt)
        return result.scalar_one_or_none()

    # ====================== DELETE ======================
    def delete(self, db: Session, instance: T) -> None:
        db.delete(instance)

    def delete_by_id(self, db: Session, id_value: Any) -> bool:
        stmt = (
            delete(self.model).where(self.model.id == id_value).returning(self.model.id)
        )
        result = self._execute(db, stmt)
        return result.scalar_one() is not None
