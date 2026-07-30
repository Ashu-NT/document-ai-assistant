from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base
from src.infrastructure.db.orm_models.extraction._extraction_entity_columns_mixin import (
    ExtractionEntityColumnsMixin,
)


class MaintenanceIntervalORM(ExtractionEntityColumnsMixin, Base):
    __tablename__ = "maintenance_intervals"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    interval: Mapped[str] = mapped_column(String, nullable=False)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    # SET NULL: the interval fact remains valid even without a specific
    # maintenance-task link.
    maintenance_task_id: Mapped[str | None] = mapped_column(
        ForeignKey("maintenance_tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
