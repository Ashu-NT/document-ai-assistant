from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class MaintenanceTaskORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "maintenance_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    interval: Mapped[str | None] = mapped_column(String, nullable=True)

    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    equipment_id: Mapped[str | None] = mapped_column(String, nullable=True)
