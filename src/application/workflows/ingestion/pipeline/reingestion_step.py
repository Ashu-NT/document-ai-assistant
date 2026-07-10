from __future__ import annotations

from src.application.services.document import DocumentLookupService
from src.application.workflows.ingestion.ingestion_exceptions import (
    DocumentNotFoundForReingestionError,
    ReingestionNotSupportedError,
)
from src.application.workflows.ingestion.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.reingestion_request import ReingestionRequest
from src.shared.activity import ActivityContext


class ReingestionStep:
    """Resolves a `ReingestionRequest` against the currently persisted
    document graph and builds the equivalent `IngestionRequest` for
    `IngestionWorkflow.run` to execute.
    """

    def __init__(self, *, document_lookup_service: DocumentLookupService | None) -> None:
        self.document_lookup_service = document_lookup_service

    def prepare_request(
        self,
        request: ReingestionRequest,
        *,
        activity_context: ActivityContext | None = None,
    ) -> IngestionRequest:
        if self.document_lookup_service is None:
            raise ReingestionNotSupportedError(
                "Reingestion requires a document_lookup_service dependency, "
                "which this IngestionWorkflow instance was not constructed with.",
                error_code="reingestion_not_supported",
                details={"document_id": request.document_id},
            )

        existing_graph = self.document_lookup_service.get_document_graph(
            request.document_id,
            activity_context=activity_context,
        )
        if existing_graph is None:
            raise DocumentNotFoundForReingestionError(
                "Reingestion target document does not exist.",
                error_code="reingestion.document_not_found",
                details={"document_id": request.document_id},
            )

        preserved_document_id = (
            request.document_id if request.preserve_document_id else None
        )
        return IngestionRequest(
            file_path=existing_graph.document.file_path,
            document_type=existing_graph.document.document_type.value,
            title=existing_graph.document.title,
            source_name=existing_graph.document.source_name,
            metadata=dict(request.metadata),
            force=True,
            run_quality_checks=request.run_quality_checks,
            requested_by=request.requested_by,
            correlation_id=request.correlation_id,
            preserve_document_id=preserved_document_id,
        )
