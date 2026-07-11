from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class TroubleshootingEntryORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "troubleshooting_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    symptom: Mapped[str] = mapped_column(Text, nullable=False)
    cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    remedy: Mapped[str | None] = mapped_column(Text, nullable=True)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    equipment_id: Mapped[str | None] = mapped_column(
        ForeignKey("equipment_info.id"),
        nullable=True,
        index=True,
    )
