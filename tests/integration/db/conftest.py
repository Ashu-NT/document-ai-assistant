import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from collections.abc import Generator

from src.infrastructure.db import orm_models  # noqa: F401
from src.infrastructure.db.base import Base
from src.infrastructure.db.schema_management import ensure_database_schema
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import ChunkType, DocumentType, ModelProcessingMetadata, SourceLocation
from src.domain.document import Document, DocumentChunk, DocumentGraph, DocumentHashes

@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
    )

    # Mirrors src/infrastructure/db/session.py's production engine: without
    # this, FK constraints (and their ondelete= policies) are silently
    # unenforced for every integration test using this fixture, regardless
    # of what's declared on the ORM models.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    ensure_database_schema(engine)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    testing_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def db_uow(db_session: Session) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(db_session)


@pytest.fixture
def seed_document_with_chunks(
    db_uow: SqlAlchemyUnitOfWork,
    document_id: str,
):
    """Factory fixture: seed a real documents row plus one chunks row per
    given chunk id, for tests whose fixtures reference a document/chunk by
    id (e.g. via source_chunk_id) without creating it themselves, now that
    those FKs are actually enforced. Not autouse -- tests like
    test_unit_of_work.py's rollback tests assert nothing persists, so
    seeding must be opt-in per test module rather than global.
    """

    def _seed(chunk_ids: list[str]) -> None:
        graph = DocumentGraph(
            document=Document(
                document_id=document_id,
                file_name="baseline.pdf",
                file_path="data/baseline.pdf",
                hashes=DocumentHashes(file_hash="baseline_fh", content_hash="baseline_ch"),
                document_type=DocumentType.MANUAL,
            )
        )
        for index, chunk_id in enumerate(chunk_ids):
            graph.add_chunk(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    section_id=None,
                    content="baseline seed chunk",
                    chunk_type=ChunkType.GENERAL,
                    sequence_number=index + 1,
                    chunk_index=index,
                    chunk_total=len(chunk_ids),
                    source=SourceLocation(page_start=1, page_end=1),
                )
            )
        db_uow.documents.save_document_graph(graph)
        db_uow.commit()

    return _seed


@pytest.fixture
def seeded_document_and_chunk(
    seed_document_with_chunks,
    chunk_id: str,
) -> None:
    seed_document_with_chunks([chunk_id])


@pytest.fixture
def sample_document_classification(document_id: str) -> DocumentClassification:
    result = ClassificationResult(
        classification_id="classification_doc_001",
        document_id=document_id,
        predicted_label=DocumentType.MANUAL.value,
        confidence_score=0.9,
        rationale="Document contains maintenance procedures.",
        evidence=["maintenance", "procedure", "safety"],
        processing_metadata=ModelProcessingMetadata(
            model_name="qwen3:8b",
            model_type="classification",
            prompt_version="v1",
            confidence=0.9,
        ),
    )

    return DocumentClassification(
        document_id=document_id,
        document_type=DocumentType.MANUAL,
        result=result,
    )
