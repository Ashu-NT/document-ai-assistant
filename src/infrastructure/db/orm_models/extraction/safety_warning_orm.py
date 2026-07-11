from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class SafetyWarningORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "safety_warnings"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    warning_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
