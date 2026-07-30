from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class ProcedureORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "procedures"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    title: Mapped[str] = mapped_column(String, nullable=False)
    procedure_type: Mapped[str] = mapped_column(
        String, nullable=False, server_default="unknown", index=True
    )
    steps_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    # SET NULL: the procedure fact remains valid/useful even without a
    # specific equipment link.
    equipment_id: Mapped[str | None] = mapped_column(
        ForeignKey("equipment_info.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
