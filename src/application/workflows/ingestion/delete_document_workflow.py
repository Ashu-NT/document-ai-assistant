from __future__ import annotations

from src.application.contracts import UnitOfWork
from src.application.contracts.retrieval import VectorStore
from src.application.workflows.ingestion.ingestion_exceptions import (
    DocumentNotFoundForDeletionError,
)
from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.execution import tracked_action


class DeleteDocumentWorkflow:
    def __init__(
        self,
        *,
        unit_of_work: UnitOfWork,
        vector_store: VectorStore,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.vector_store = vector_store

    @tracked_action(
        action="document.delete.requested",
        entity_type="document",
        activity=True,
        audit=True,
        event=False,
    )
    def run(
        self,
        document_id: str,
        *,
        activity_context: ActivityContext | None = None,
        audit_context: AuditContext | None = None,
    ) -> None:
        existing_entry = self.unit_of_work.documents.get_document_entry(document_id)
        if existing_entry is None:
            raise DocumentNotFoundForDeletionError(
                "Document to delete does not exist.",
                error_code="delete.document_not_found",
                details={"document_id": document_id},
            )

        try:
            self.unit_of_work.extractions.delete_by_document(document_id)
            self.unit_of_work.classifications.delete_document_classification(
                document_id
            )
            self.unit_of_work.documents.delete_document(document_id)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

        # Vector cleanup runs after the SQL transaction commits: SQLite here
        # has no FK enforcement, so leaving `chunk_vectors` rows momentarily
        # pointing at a deleted document is safe, and this ordering means a
        # Qdrant failure never leaves the document half-deleted in SQL.
        self.vector_store.delete_document_vectors(document_id)
        self.unit_of_work.commit()
