from __future__ import annotations

from src.application.contracts import UnitOfWork
from src.application.contracts.retrieval import VectorStore
from src.application.workflows.ingestion.models.ingestion_exceptions import (
    DocumentNotFoundForDeletionError,
)
from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.execution import ActionResult, tracked_action


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
    ) -> ActionResult:
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

        return ActionResult(
            entity_type="document",
            entity_id=document_id,
            message="Document deleted.",
            payload={"document_id": document_id},
            # existing_entry was already loaded above to check the document
            # exists, before anything was deleted -- capturing it here as
            # before_state is free (no extra read) and is the only record of
            # what was actually deleted beyond the bare document_id.
            before_state={
                "document_id": existing_entry.document_id,
                "title": existing_entry.title,
                "file_name": existing_entry.file_name,
                "file_path": existing_entry.file_path,
                "document_type": existing_entry.document_type,
                "language": existing_entry.language,
                "page_count": existing_entry.page_count,
                "chunk_count": existing_entry.chunk_count,
                "section_count": existing_entry.section_count,
                "identifier_count": existing_entry.identifier_count,
                "table_count": existing_entry.table_count,
                "picture_count": existing_entry.picture_count,
                "created_at": existing_entry.created_at.isoformat()
                if existing_entry.created_at
                else None,
            },
        )
