from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.application.contracts.document import IngestionRunRepository
from src.domain.common import IngestionStatus
from src.domain.workflow import IngestionRun
from src.infrastructure.db.mappers import IngestionRunMapper
from src.infrastructure.db.orm_models import IngestionRunORM
from src.infrastructure.db.repositories.common import update_orm_from_orm
from src.shared.exceptions import DatabaseError


class SqlAlchemyIngestionRunRepository(IngestionRunRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, ingestion_run: IngestionRun) -> None:
        try:
            self.session.add(IngestionRunMapper.to_orm(ingestion_run))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to create ingestion run.",
                details={"run_id": ingestion_run.run_id},
            ) from exc

    def get(self, run_id: str) -> IngestionRun | None:
        try:
            orm = self.session.get(IngestionRunORM, run_id)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load ingestion run.",
                details={"run_id": run_id},
            ) from exc

        if orm is None:
            return None

        return IngestionRunMapper.to_domain(orm)

    def update(self, ingestion_run: IngestionRun) -> None:
        try:
            existing = self.session.get(IngestionRunORM, ingestion_run.run_id)
            updated = IngestionRunMapper.to_orm(ingestion_run)

            if existing is None:
                self.session.add(updated)
                return

            update_orm_from_orm(existing, updated)

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to update ingestion run.",
                details={"run_id": ingestion_run.run_id},
            ) from exc

    def mark_status(
        self,
        run_id: str,
        status: IngestionStatus,
        error_message: str | None = None,
    ) -> None:
        try:
            existing = self.session.get(IngestionRunORM, run_id)

            if existing is None:
                raise DatabaseError(
                    "Ingestion run not found.",
                    details={"run_id": run_id},
                )

            existing.status = status.value
            existing.error_message = error_message

        except DatabaseError:
            raise
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to update ingestion run status.",
                details={
                    "run_id": run_id,
                    "status": status.value,
                },
            ) from exc