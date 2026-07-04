from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import QdrantClient

from src.application.contracts.ai import EmbeddingProvider
from src.application.services.document import DocumentLookupService
from src.application.services.document_exploration import DocumentExplorationService
from src.application.workflows.retrieval import RetrievalWorkflow
from src.infrastructure.retrieval.vector import QdrantVectorStore


@dataclass(slots=True)
class RetrievalRuntime:
    """The SQL+dense hybrid retrieval stack, fully wired.

    Bundles the retrieval workflow with the supporting services callers
    commonly need alongside it, plus the resources (`vector_store`,
    `qdrant_client`, `embedding_provider`) that other runtime pieces
    (e.g. a lazily-built ingestion runtime) may need to reuse rather than
    opening a second connection.
    """

    retrieval_workflow: RetrievalWorkflow
    document_lookup_service: DocumentLookupService
    exploration_service: DocumentExplorationService
    vector_store: QdrantVectorStore
    qdrant_client: QdrantClient
    embedding_provider: EmbeddingProvider
