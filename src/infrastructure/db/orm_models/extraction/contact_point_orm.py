from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class ContactPointORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "contact_points"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    contact_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_name: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    owner_entity_type: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
