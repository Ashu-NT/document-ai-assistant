import pytest

from src.application.workflows.ingestion import (
    DeleteDocumentWorkflow,
    DocumentNotFoundForDeletionError,
)


class FakeDocumentRepository:
    def __init__(self, *, existing_document_id: str | None, call_log: list) -> None:
        self.existing_document_id = existing_document_id
        self.call_log = call_log
        self.delete_calls = []

    def get_document_entry(self, document_id: str):
        if document_id == self.existing_document_id:
            return object()
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

    def delete_document_vectors(self, document_id: str) -> None:
        self.delete_calls.append(document_id)
        self.call_log.append(("vectors", document_id))


def test_delete_document_workflow_raises_when_document_not_found() -> None:
    unit_of_work = FakeUnitOfWork(existing_document_id=None)
    vector_store = FakeVectorStore(unit_of_work.call_log)
    workflow = DeleteDocumentWorkflow(unit_of_work=unit_of_work, vector_store=vector_store)

    with pytest.raises(DocumentNotFoundForDeletionError):
        workflow.run("doc_missing")

    assert unit_of_work.extractions.delete_calls == []
    assert unit_of_work.classifications.delete_calls == []
    assert unit_of_work.documents.delete_calls == []
    assert vector_store.delete_calls == []
    assert unit_of_work.commit_count == 0


def test_delete_document_workflow_deletes_all_document_data_in_order() -> None:
    unit_of_work = FakeUnitOfWork(existing_document_id="doc_001")
    vector_store = FakeVectorStore(unit_of_work.call_log)
    workflow = DeleteDocumentWorkflow(unit_of_work=unit_of_work, vector_store=vector_store)

    workflow.run("doc_001")

    assert unit_of_work.extractions.delete_calls == ["doc_001"]
    assert unit_of_work.classifications.delete_calls == ["doc_001"]
    assert unit_of_work.documents.delete_calls == ["doc_001"]
    assert vector_store.delete_calls == ["doc_001"]
    assert unit_of_work.commit_count == 2
    assert unit_of_work.rollback_count == 0
    # extraction and classification rows must be gone before the document
    # row itself, and vectors are cleaned up only after the SQL commit.
    assert unit_of_work.call_log == [
        ("extractions", "doc_001"),
        ("classifications", "doc_001"),
        ("documents", "doc_001"),
        ("vectors", "doc_001"),
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
