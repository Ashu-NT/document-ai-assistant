from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.application.contracts.events import EventRepository
from src.infrastructure.db.mappers import EventEnvelopeMapper
from src.infrastructure.db.orm_models import EventEnvelopeORM
from src.shared.events import EventEnvelope
from src.shared.exceptions import DatabaseError


class SqlAlchemyEventRepository(EventRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, event: EventEnvelope) -> None:
        try:
            self.session.add(EventEnvelopeMapper.to_orm(event))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save event envelope.",
                details={
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "aggregate_type": event.aggregate_type,
                    "aggregate_id": event.aggregate_id,
                },
            ) from exc

    def list_by_aggregate(
        self,
        aggregate_type: str,
        aggregate_id: str,
        limit: int = 50,
    ) -> list[EventEnvelope]:
        try:
            statement = (
                select(EventEnvelopeORM)
                .where(EventEnvelopeORM.aggregate_type == aggregate_type)
                .where(EventEnvelopeORM.aggregate_id == aggregate_id)
                .order_by(desc(EventEnvelopeORM.occurred_at))
                .limit(limit)
            )

            rows = self.session.execute(statement).scalars().all()

            return [EventEnvelopeMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list event envelopes by aggregate.",
                details={
                    "aggregate_type": aggregate_type,
                    "aggregate_id": aggregate_id,
                    "limit": limit,
                },
            ) from exc