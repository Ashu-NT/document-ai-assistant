from __future__ import annotations

from src.application.contracts import UnitOfWork
from src.application.contracts.retrieval import VectorStore
from src.application.workflows.ingestion.models.ingestion_exceptions import (
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

        # Captured before the SQL delete: FK constraints are enforced now
        # (PRAGMA foreign_keys=ON), so the `chunk_vectors` mapping rows must
        # be gone before `chunks`/`documents` are deleted, which means the
        # point IDs have to be read first.
        point_ids = self.unit_of_work.vector_mappings.list_qdrant_point_ids_by_document(
            document_id
        )

        try:
            self.unit_of_work.vector_mappings.delete_document_mappings(document_id)
            self.unit_of_work.extractions.delete_by_document(document_id)
            self.unit_of_work.classifications.delete_document_classification(
                document_id
            )
            self.unit_of_work.documents.delete_document(document_id)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

        # Qdrant cleanup runs after the SQL transaction commits, using the
        # point IDs captured above (the SQL mapping rows are already gone):
        # a Qdrant failure here never leaves the document half-deleted in
        # SQL, only inert orphaned vectors in Qdrant.
        self.vector_store.delete_vector_points(point_ids)
