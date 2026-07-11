from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class SparePartORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "spare_parts"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    part_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[str | None] = mapped_column(String, nullable=True)

    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer_name: Mapped[str | None] = mapped_column(String, nullable=True)
