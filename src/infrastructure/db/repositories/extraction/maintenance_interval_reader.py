from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import MaintenanceInterval
from src.infrastructure.db.mappers import MaintenanceIntervalMapper
from src.infrastructure.db.orm_models import MaintenanceIntervalORM
from src.shared.exceptions import DatabaseError


class MaintenanceIntervalReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_maintenance_intervals(
        self,
        document_id: str | None = None,
    ) -> list[MaintenanceInterval]:
        try:
            statement = select(MaintenanceIntervalORM)

            if document_id is not None:
                statement = statement.where(
                    MaintenanceIntervalORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [MaintenanceIntervalMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list maintenance intervals.",
                details={"document_id": document_id},
            ) from exc

    def list_by_maintenance_task_id(
        self,
        maintenance_task_id: str,
    ) -> list[MaintenanceInterval]:
        try:
            statement = select(MaintenanceIntervalORM).where(
                MaintenanceIntervalORM.maintenance_task_id == maintenance_task_id
            )

            rows = self.session.execute(statement).scalars().all()

            return [MaintenanceIntervalMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list maintenance intervals for maintenance task.",
                details={"maintenance_task_id": maintenance_task_id},
            ) from exc

    def search_maintenance_intervals(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[MaintenanceInterval]:
        try:
            pattern = f"%{query}%"
            statement = select(MaintenanceIntervalORM).where(
                or_(
                    MaintenanceIntervalORM.interval.ilike(pattern),
                    MaintenanceIntervalORM.component_name.ilike(pattern),
                )
            )

            if document_id is not None:
                statement = statement.where(
                    MaintenanceIntervalORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [MaintenanceIntervalMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search maintenance intervals.",
                details={"query": query, "document_id": document_id},
            ) from exc
