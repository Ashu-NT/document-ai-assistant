from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class SpecificationORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "specifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    parameter: Mapped[str] = mapped_column(String, nullable=False, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
