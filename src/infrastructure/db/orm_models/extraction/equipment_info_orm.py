from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class EquipmentInfoORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "equipment_info"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    model_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    manufacturer_name: Mapped[str | None] = mapped_column(String, nullable=True)
