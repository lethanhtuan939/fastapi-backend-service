from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String, func
from datetime import datetime


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict:
        """Convert SQLAlchemy model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name of the model."""
        return cls.__tablename__

    @classmethod
    def get_primary_key(cls) -> str:
        """Get the primary key column name of the model."""
        for column in cls.__table__.columns:
            if column.primary_key:
                return column.name
        return ""

    @classmethod
    def get_columns(cls) -> list[str]:
        """Get the list of column names of the model."""
        return [c.name for c in cls.__table__.columns]

    @classmethod
    def get_column_types(cls) -> dict[str, str]:
        """Get the dictionary of column names and their types of the model."""
        return {c.name: str(c.type) for c in cls.__table__.columns}
