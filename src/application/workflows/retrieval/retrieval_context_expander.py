from src.application.services.document import DocumentLookupService
from src.application.workflows.retrieval.context_chunk_converter import (
    to_retrieved_chunk,
)
from src.application.workflows.retrieval.context_expansion.document_chunk_index import (
    DocumentChunkIndex,
)
from src.application.workflows.retrieval.context_priority_policy import (
    context_priority,
)
from src.application.workflows.retrieval.context_relation_classifier import (
    classify_context_relation,
)
from src.application.workflows.retrieval.retrieval_context_assembler import (
    RetrievalContextAssembler,
    RetrievalContextCandidate,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


def _default_neighbor_window() -> int:
    try:
        from src.config.settings import retrieval_settings
        return retrieval_settings.context_neighbor_window
    except Exception:
        return 1


def _default_max_context_chunks() -> int:
    try:
        from src.config.settings import retrieval_settings
        return retrieval_settings.context_max_chunks
    except Exception:
        return 8


class RetrievalContextExpander:
    def __init__(
        self,
        document_lookup_service: DocumentLookupService,
        *,
        neighbor_window: int | None = None,
        max_context_chunks: int | None = None,
        query_intent_inferer: RetrievalQueryIntentInferer | None = None,
        context_assembler: RetrievalContextAssembler | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.neighbor_window = max(
            0,
            neighbor_window if neighbor_window is not None else _default_neighbor_window(),
        )
        self.max_context_chunks = max(
            1,
            max_context_chunks if max_context_chunks is not None else _default_max_context_chunks(),
        )
        self.query_intent_inferer = (
            query_intent_inferer or RetrievalQueryIntentInferer()
        )
        self.context_assembler = context_assembler or RetrievalContextAssembler()

    def expand(
        self,
        chunks: list[RetrievedChunk],
        query: RetrievalQuery | None = None,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return list(chunks)

        query_intent = self.query_intent_inferer.resolve(query)
        chunk_cache: dict[str, list] = {}
        index_cache: dict[str, DocumentChunkIndex] = {}
        candidates_by_anchor_id: dict[str, list[RetrievalContextCandidate]] = {}

        for anchor_chunk in chunks:
            document_chunks = chunk_cache.get(anchor_chunk.document_id)
            if document_chunks is None:
                document_chunks = self.document_lookup_service.list_chunks_by_document(
                    anchor_chunk.document_id
                )
                chunk_cache[anchor_chunk.document_id] = document_chunks
                index_cache[anchor_chunk.document_id] = DocumentChunkIndex.build(
                    document_chunks
                )

            chunk_index = index_cache[anchor_chunk.document_id]
            anchor_document_chunk = chunk_index.by_chunk_id.get(anchor_chunk.chunk_id)
            if anchor_document_chunk is None:
                continue

            candidates_by_anchor_id[anchor_chunk.chunk_id] = (
                self._select_context_chunks(
                    anchor_chunk=anchor_chunk,
                    chunk_index=chunk_index,
                    anchor_document_chunk=anchor_document_chunk,
                    query_intent=query_intent,
                )
            )

        return self.context_assembler.assemble(
            anchors=list(chunks),
            candidates_by_anchor_id=candidates_by_anchor_id,
            max_context_chunks=self.max_context_chunks,
            query_intent=query_intent,
            to_retrieved_chunk=lambda candidate: to_retrieved_chunk(
                document_chunk=candidate.document_chunk,
                anchor_chunk=candidate.anchor_chunk,
                relation=candidate.relation,
                distance=candidate.distance,
                query_intent=query_intent,
            ),
        )

    def _select_context_chunks(
        self,
        *,
        anchor_chunk: RetrievedChunk,
        chunk_index: DocumentChunkIndex,
        anchor_document_chunk,
        query_intent: RetrievalQueryIntent,
    ) -> list[RetrievalContextCandidate]:
        candidates_by_chunk_id: dict[str, RetrievalContextCandidate] = {}

        for document_chunk in chunk_index.plausible_candidates(
            anchor_document_chunk,
            neighbor_window=self.neighbor_window,
        ):
            if document_chunk.chunk_id == anchor_document_chunk.chunk_id:
                continue

            relation, distance = classify_context_relation(
                anchor_document_chunk=anchor_document_chunk,
                document_chunk=document_chunk,
                neighbor_window=self.neighbor_window,
            )
            if relation is None:
                continue

            candidate = RetrievalContextCandidate(
                anchor_chunk=anchor_chunk,
                document_chunk=document_chunk,
                relation=relation,
                distance=distance,
                priority=context_priority(
                    relation=relation,
                    query_intent=query_intent,
                    document_chunk=document_chunk,
                ),
            )
            existing = candidates_by_chunk_id.get(document_chunk.chunk_id)
            if existing is None or self._is_better_candidate(candidate, existing):
                candidates_by_chunk_id[document_chunk.chunk_id] = candidate

        return sorted(
            candidates_by_chunk_id.values(),
            key=lambda candidate: (
                -candidate.priority,
                candidate.distance,
                candidate.document_chunk.sequence_number,
            ),
        )

    @staticmethod
    def _is_better_candidate(
        candidate: RetrievalContextCandidate,
        existing: RetrievalContextCandidate,
    ) -> bool:
        if candidate.priority != existing.priority:
            return candidate.priority > existing.priority
        return candidate.distance < existing.distance
