from datetime import datetime, timezone

import pytest

from src.application.contracts.document import DocumentCatalogEntry
from src.application.workflows.ingestion import (
    DeleteDocumentWorkflow,
    DocumentNotFoundForDeletionError,
)


def _make_document_entry(document_id: str) -> DocumentCatalogEntry:
    return DocumentCatalogEntry(
        document_id=document_id,
        title="Hydraulic Pump Manual",
        file_name="pump_manual.pdf",
        file_path="data/input/pump_manual.pdf",
        document_type="manual",
        language="en",
        page_count=42,
        chunk_count=10,
        section_count=3,
        identifier_count=5,
        table_count=2,
        picture_count=1,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


class FakeDocumentRepository:
    def __init__(self, *, existing_document_id: str | None, call_log: list) -> None:
        self.existing_document_id = existing_document_id
        self.call_log = call_log
        self.delete_calls = []

    def get_document_entry(self, document_id: str):
        if document_id == self.existing_document_id:
            return _make_document_entry(document_id)
        return None

    def delete_document(self, document_id: str) -> None:
        self.delete_calls.append(document_id)
        self.call_log.append(("documents", document_id))


class FailingDocumentRepository(FakeDocumentRepository):
    def delete_document(self, document_id: str) -> None:
        raise RuntimeError("boom")


class FakeExtractionRepository:
    def __init__(self, call_log: list) -> None:
        self.call_log = call_log
        self.delete_calls = []

    def delete_by_document(self, document_id: str) -> None:
        self.delete_calls.append(document_id)
        self.call_log.append(("extractions", document_id))


class FakeClassificationRepository:
    def __init__(self, call_log: list) -> None:
        self.call_log = call_log
        self.delete_calls = []

    def delete_document_classification(self, document_id: str) -> None:
        self.delete_calls.append(document_id)
        self.call_log.append(("classifications", document_id))


class FakeVectorMappingRepository:
    def __init__(self, call_log: list, *, point_ids: list[str] | None = None) -> None:
        self.call_log = call_log
        self.point_ids = point_ids if point_ids is not None else ["point_1"]
        self.delete_calls = []

    def list_qdrant_point_ids_by_document(self, document_id: str) -> list[str]:
        self.call_log.append(("list_vector_mappings", document_id))
        return self.point_ids

    def delete_document_mappings(self, document_id: str) -> None:
        self.delete_calls.append(document_id)
        self.call_log.append(("vector_mappings", document_id))


class FakeUnitOfWork:
    def __init__(
        self,
        *,
        existing_document_id: str | None,
        document_repository=None,
    ) -> None:
        self.call_log: list = []
        self.documents = document_repository or FakeDocumentRepository(
            existing_document_id=existing_document_id, call_log=self.call_log
        )
        self.extractions = FakeExtractionRepository(self.call_log)
        self.classifications = FakeClassificationRepository(self.call_log)
        self.vector_mappings = FakeVectorMappingRepository(self.call_log)
        self.commit_count = 0
        self.rollback_count = 0

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1


class FakeVectorStore:
    def __init__(self, call_log: list) -> None:
        self.call_log = call_log
        self.delete_calls = []

    def delete_vector_points(self, point_ids: list[str]) -> None:
        self.delete_calls.append(point_ids)
        self.call_log.append(("vectors", point_ids))


def test_delete_document_workflow_raises_when_document_not_found() -> None:
    unit_of_work = FakeUnitOfWork(existing_document_id=None)
    vector_store = FakeVectorStore(unit_of_work.call_log)
    workflow = DeleteDocumentWorkflow(unit_of_work=unit_of_work, vector_store=vector_store)

    with pytest.raises(DocumentNotFoundForDeletionError):
        workflow.run("doc_missing")

    assert unit_of_work.extractions.delete_calls == []
    assert unit_of_work.classifications.delete_calls == []
    assert unit_of_work.documents.delete_calls == []
    assert unit_of_work.vector_mappings.delete_calls == []
    assert vector_store.delete_calls == []
    assert unit_of_work.commit_count == 0


def test_delete_document_workflow_deletes_all_document_data_in_order() -> None:
    unit_of_work = FakeUnitOfWork(existing_document_id="doc_001")
    vector_store = FakeVectorStore(unit_of_work.call_log)
    workflow = DeleteDocumentWorkflow(unit_of_work=unit_of_work, vector_store=vector_store)

    result = workflow.run("doc_001")

    assert result.entity_type == "document"
    assert result.entity_id == "doc_001"
    assert result.before_state == {
        "document_id": "doc_001",
        "title": "Hydraulic Pump Manual",
        "file_name": "pump_manual.pdf",
        "file_path": "data/input/pump_manual.pdf",
        "document_type": "manual",
        "language": "en",
        "page_count": 42,
        "chunk_count": 10,
        "section_count": 3,
        "identifier_count": 5,
        "table_count": 2,
        "picture_count": 1,
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    assert unit_of_work.extractions.delete_calls == ["doc_001"]
    assert unit_of_work.classifications.delete_calls == ["doc_001"]
    assert unit_of_work.documents.delete_calls == ["doc_001"]
    assert unit_of_work.vector_mappings.delete_calls == ["doc_001"]
    assert vector_store.delete_calls == [["point_1"]]
    assert unit_of_work.commit_count == 1
    assert unit_of_work.rollback_count == 0
    # Qdrant point IDs are read before anything is deleted (the mapping
    # rows won't exist to query afterward); vector_mappings is deleted
    # within the same SQL transaction as everything else, before the
    # chunks/document rows it references (FK ordering); Qdrant point
    # deletion itself only happens after that transaction commits.
    assert unit_of_work.call_log == [
        ("list_vector_mappings", "doc_001"),
        ("vector_mappings", "doc_001"),
        ("extractions", "doc_001"),
        ("classifications", "doc_001"),
        ("documents", "doc_001"),
        ("vectors", ["point_1"]),
    ]


def test_delete_document_workflow_rolls_back_when_sql_delete_fails() -> None:
    call_log: list = []
    failing_documents = FailingDocumentRepository(
        existing_document_id="doc_001", call_log=call_log
    )
    unit_of_work = FakeUnitOfWork(
        existing_document_id="doc_001",
        document_repository=failing_documents,
    )
    vector_store = FakeVectorStore(unit_of_work.call_log)
    workflow = DeleteDocumentWorkflow(unit_of_work=unit_of_work, vector_store=vector_store)

    with pytest.raises(RuntimeError):
        workflow.run("doc_001")

    assert unit_of_work.rollback_count == 1
    assert unit_of_work.commit_count == 0
    assert vector_store.delete_calls == []
