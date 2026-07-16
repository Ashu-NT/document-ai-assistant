from src.application.services.document import DocumentLookupService
from src.application.workflows.question_answering.evidence.table_evidence_hydrator import (
    TableEvidenceHydrator,
)
from src.application.workflows.question_answering.evidence.table_focused_evidence_pruner import (
    TableFocusedEvidencePruner,
)
from src.application.workflows.retrieval.deduplication.retrieved_chunk_deduplicator import (
    RetrievedChunkDeduplicator,
)
from src.domain.document import DocumentGraph
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class FinalEvidencePreparer:
    def __init__(
        self,
        *,
        document_lookup_service: DocumentLookupService | None = None,
        table_evidence_hydrator: TableEvidenceHydrator | None = None,
        deduplicator: RetrievedChunkDeduplicator | None = None,
        table_focused_evidence_pruner: TableFocusedEvidencePruner | None = None,
    ) -> None:
        self._document_lookup_service = document_lookup_service
        self._table_evidence_hydrator = (
            table_evidence_hydrator or TableEvidenceHydrator()
        )
        self._deduplicator = deduplicator or RetrievedChunkDeduplicator()
        self._table_focused_evidence_pruner = (
            table_focused_evidence_pruner or TableFocusedEvidencePruner()
        )

    def prepare(
        self,
        *,
        query: RetrievalQuery | None,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        prepared_chunks = list(chunks)
        graphs_by_document_id = self._load_document_graphs(prepared_chunks)
        if graphs_by_document_id:
            prepared_chunks = self._table_evidence_hydrator.hydrate(
                chunks=prepared_chunks,
                graphs_by_document_id=graphs_by_document_id,
            )

        prepared_chunks = self._deduplicator.deduplicate(
            query=query,
            chunks=prepared_chunks,
        ).chunks
        return self._table_focused_evidence_pruner.prune(
            query=query,
            chunks=prepared_chunks,
        )

    def _load_document_graphs(
        self,
        chunks: list[RetrievedChunk],
    ) -> dict[str, DocumentGraph]:
        if self._document_lookup_service is None:
            return {}

        graphs_by_document_id: dict[str, DocumentGraph] = {}
        for document_id in dict.fromkeys(chunk.document_id for chunk in chunks):
            graph = self._document_lookup_service.get_document_graph(document_id)
            if graph is not None:
                graphs_by_document_id[document_id] = graph
        return graphs_by_document_id
