from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.application.contracts.activity import ActivityRepository
from src.domain.activity import ActivityRecord
from src.infrastructure.db.mappers import ActivityRecordMapper
from src.infrastructure.db.orm_models import ActivityRecordORM
from src.shared.exceptions import DatabaseError


class SqlAlchemyActivityRepository(ActivityRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, activity: ActivityRecord) -> None:
        try:
            self.session.add(ActivityRecordMapper.to_orm(activity))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save activity record.",
                details={
                    "activity_id": activity.activity_id,
                    "action": activity.action,
                    "entity_type": activity.entity_type,
                    "entity_id": activity.entity_id,
                },
            ) from exc

    def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
    ) -> list[ActivityRecord]:
        try:
            statement = (
                select(ActivityRecordORM)
                .where(ActivityRecordORM.entity_type == entity_type)
                .where(ActivityRecordORM.entity_id == entity_id)
                .order_by(desc(ActivityRecordORM.created_at))
                .limit(limit)
            )

            rows = self.session.execute(statement).scalars().all()

            return [ActivityRecordMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list activity records by entity.",
                details={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "limit": limit,
                },
            ) from exc