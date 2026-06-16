from typing import Protocol

from src.domain.common import IngestionStatus
from src.domain.workflow import IngestionRun


class IngestionRunRepository(Protocol):
    def create(self, ingestion_run: IngestionRun) -> None:
        ...

    def get(self, run_id: str) -> IngestionRun | None:
        ...

    def update(self, ingestion_run: IngestionRun) -> None:
        ...

    def mark_status(
        self,
        run_id: str,
        status: IngestionStatus,
        error_message: str | None = None,
    ) -> None:
        ...