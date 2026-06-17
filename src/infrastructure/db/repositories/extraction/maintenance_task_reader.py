from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import MaintenanceTask
from src.infrastructure.db.mappers import MaintenanceTaskMapper
from src.infrastructure.db.orm_models import MaintenanceTaskORM
from src.shared.exceptions import DatabaseError


class MaintenanceTaskReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_maintenance_tasks(
        self,
        document_id: str | None = None,
    ) -> list[MaintenanceTask]:
        try:
            statement = select(MaintenanceTaskORM)

            if document_id is not None:
                statement = statement.where(
                    MaintenanceTaskORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [MaintenanceTaskMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list maintenance tasks.",
                details={"document_id": document_id},
            ) from exc