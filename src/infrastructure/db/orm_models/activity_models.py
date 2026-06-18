from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ActivityRecordORM(Base):
    __tablename__ = "activity_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    entity_type: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    status: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String, nullable=False, index=True)

    actor_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    actor_type: Mapped[str] = mapped_column(String, nullable=False, default="system")

    request_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)

    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)