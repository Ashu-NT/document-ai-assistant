from __future__ import annotations

from src.application.contracts import UnitOfWork
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.domain.workflow import IngestionRun


class IngestionRunStore:
    def __init__(self, *, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def create(self, ingestion_run: IngestionRun) -> None:
        self.unit_of_work.ingestion_runs.create(ingestion_run)
        self.unit_of_work.commit()

    def update(self, ingestion_run: IngestionRun) -> None:
        self.unit_of_work.ingestion_runs.update(ingestion_run)
        self.unit_of_work.commit()

    def mark_status(
        self,
        ingestion_run: IngestionRun,
        status: IngestionStatus,
    ) -> None:
        ingestion_run.mark_status(status, error_message=None)
        self.update(ingestion_run)

    def rollback(self) -> None:
        try:
            self.unit_of_work.rollback()
        except Exception:
            return
