from typing import Any


def update_orm_from_orm(existing: Any, updated: Any) -> None:
    """
    Copy column values from one ORM instance to another.

    Used when updating an existing row without replacing the SQLAlchemy identity.
    """
    for column in existing.__table__.columns:
        column_name = column.name
        setattr(existing, column_name, getattr(updated, column_name))