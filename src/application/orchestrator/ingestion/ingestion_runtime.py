from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import QdrantClient

from src.application.contracts import UnitOfWork
from src.application.services.classification import ClassificationService
from src.application.services.document import (
    DocumentLookupService,
    DocumentRegistrationService,
    DuplicateDetectionService,
)
from src.application.workflows.classification import (
    DocumentClassificationWorkflow,
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.ingestion import DeleteDocumentWorkflow, IngestionWorkflow
from src.application.workflows.parsing import ParsingWorkflow
from src.application.workflows.parsing.builders import DocumentGraphBuilder


@dataclass(slots=True)
class IngestionRuntime:
    """Fully-wired ingestion dependency graph produced by the ingestion orchestrator.

    Bundles the canonical `IngestionWorkflow` with the supporting services
    that ingestion entrypoints commonly need alongside it (benchmark corpus
    seeding today; a production ingest CLI/tool in the future), plus the
    resources that must be released when the runtime is done (`unit_of_work`,
    `qdrant_client`).
    """

    ingestion_workflow: IngestionWorkflow
    delete_document_workflow: DeleteDocumentWorkflow
    parsing_workflow: ParsingWorkflow
    document_graph_builder: DocumentGraphBuilder
    document_registration_service: DocumentRegistrationService
    document_lookup_service: DocumentLookupService
    duplicate_detection_service: DuplicateDetectionService
    classification_service: ClassificationService
    document_classification_workflow: DocumentClassificationWorkflow
    post_classification_chunk_finalization_workflow: (
        PostClassificationChunkFinalizationWorkflow
    )
    unit_of_work: UnitOfWork
    embedding_model: str
    vector_collection: str
    qdrant_client: QdrantClient | None = None

    def close(self) -> None:
        """Release the session/client resources owned by this runtime."""
        session = getattr(self.unit_of_work, "session", None)
        if session is not None:
            session.close()

        if self.qdrant_client is None:
            return
        close = getattr(self.qdrant_client, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass
