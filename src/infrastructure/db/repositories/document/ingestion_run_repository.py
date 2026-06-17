from sqlalchemy.orm import Session

from src.application.contracts.document import IngestionRunRepository
from domain.common import IngestionStatus
from domain.workflows import IngestionRun
from infrastructure.db.mappers.workflow.ingestion_run_mapper import IngestionRunMapper
from infrastructure.db.orm_models import IngestionRunORM
from infrastructure.db.repositories.common import update_orm_from_orm


class SqlAlchemyIngestionRunRepository(IngestionRunRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, ingestion_run: IngestionRun) -> None:
        self.session.add(IngestionRunMapper.to_orm(ingestion_run))

    def get(self, run_id: str) -> IngestionRun | None:
        orm = self.session.get(IngestionRunORM, run_id)

        if orm is None:
            return None

        return IngestionRunMapper.to_domain(orm)

    def update(self, ingestion_run: IngestionRun) -> None:
        existing = self.session.get(IngestionRunORM, ingestion_run.run_id)
        updated = IngestionRunMapper.to_orm(ingestion_run)

        if existing is None:
            self.session.add(updated)
            return

        update_orm_from_orm(existing, updated)

    def mark_status(
        self,
        run_id: str,
        status: IngestionStatus,
        error_message: str | None = None,
    ) -> None:
        existing = self.session.get(IngestionRunORM, run_id)

        if existing is None:
            raise ValueError(f"Ingestion run not found: {run_id}")

        existing.status = status.value
        existing.error_message = error_message