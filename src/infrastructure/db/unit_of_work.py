from types import TracebackType
from typing import Self

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.application.contracts.unit_of_work import UnitOfWork
from src.infrastructure.db.repositories.classification import (
    SqlAlchemyClassificationRepository,
)
from src.infrastructure.db.repositories.document import (
    SqlAlchemyDocumentRepository,
    SqlAlchemyIngestionRunRepository,
)
from src.infrastructure.db.repositories.extraction import (
    SqlAlchemyExtractionRepository,
)
from src.infrastructure.db.repositories.memory import (
    SqlAlchemyMemoryRepository,
)
from src.infrastructure.db.repositories.activity import (
    SqlAlchemyActivityRepository,
)
from src.infrastructure.db.repositories.audit import SqlAlchemyAuditRepository
from src.infrastructure.db.repositories.events import SqlAlchemyEventRepository
from src.shared.exceptions import DatabaseError
from src.infrastructure.db.repositories.retrieval import SqlKeywordRepository, SqlAlchemyVectorMappingRepository

class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        self.session = session

        self.documents = SqlAlchemyDocumentRepository(session)
        self.classifications = SqlAlchemyClassificationRepository(session)
        self.extractions = SqlAlchemyExtractionRepository(session)
        self.memory = SqlAlchemyMemoryRepository(session)
        self.ingestion_runs = SqlAlchemyIngestionRunRepository(session)
        self.activity = SqlAlchemyActivityRepository(session)
        self.audit = SqlAlchemyAuditRepository(session)
        self.events = SqlAlchemyEventRepository(session)
        self.keyword_index = SqlKeywordRepository(session)
        self.vector_mappings = SqlAlchemyVectorMappingRepository(session)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
            return

        self.commit()

    def commit(self) -> None:
        try:
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise DatabaseError(
                "Failed to commit database transaction.",
            ) from exc

    def rollback(self) -> None:
        try:
            self.session.rollback()
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to rollback database transaction.",
            ) from exc