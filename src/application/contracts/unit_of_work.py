from types import TracebackType
from typing import Protocol, Self

from src.application.contracts.classification import ClassificationRepository
from src.application.contracts.document import DocumentRepository, IngestionRunRepository
from src.application.contracts.extraction import ExtractionRepository
from src.application.contracts.memory import MemoryRepository


class UnitOfWork(Protocol):
    documents: DocumentRepository
    classifications: ClassificationRepository
    extractions: ExtractionRepository
    memory: MemoryRepository
    ingestion_runs: IngestionRunRepository

    def __enter__(self) -> Self:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...