from src.application.services.document import DocumentLookupService
from src.application.workflows.retrieval.context_expansion.context_chunk_converter import (
    to_retrieved_chunk,
)
from src.application.workflows.retrieval.query_analysis.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.domain.document import DocumentGraph
from src.domain.retrieval import RetrievalQuery, RetrievedChunk

_REFERENCED_PROCEDURE_RELATION = "referenced_procedure"
_REFERENCED_PROCEDURE_DISTANCE = 1


class CrossReferenceContextExpander:
    """Surfaces the procedure a retrieved chunk explicitly points to via an
    inline same-document reference ("(-> Page 1062)", detected/resolved at
    ingestion time by `ChunkCrossReferenceLinker`), so the referenced
    content reaches the LLM alongside the referencing chunk instead of only
    the page number.

    Must be composed into `RetrievalWorkflow.run()` alongside (not inside)
    `RetrievalContextExpander`, *before* `context_guardrail_chain.run()`
    computes `approved_chunks` -- a chunk introduced any later (e.g. inside
    `FinalEvidencePreparer`) is filtered back out by
    `StructuredFactJoiner.join()`'s `approved_chunk_ids` check before it ever
    reaches the LLM. See the cross-reference linking plan doc
    (`outputs/architecture/chunk_cross_reference_linking_plan.md`) for the
    full trace of that constraint.
    """

    def __init__(
        self,
        document_lookup_service: DocumentLookupService,
        *,
        query_intent_inferer: RetrievalQueryIntentInferer | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.query_intent_inferer = (
            query_intent_inferer or RetrievalQueryIntentInferer()
        )

    def expand(
        self,
        chunks: list[RetrievedChunk],
        query: RetrievalQuery | None = None,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return list(chunks)

        query_intent = self.query_intent_inferer.resolve(query)
        graph_cache: dict[str, DocumentGraph | None] = {}
        present_chunk_ids = {chunk.chunk_id for chunk in chunks}
        added_chunks: list[RetrievedChunk] = []

        for anchor_chunk in chunks:
            graph = self._graph_for_document(anchor_chunk.document_id, graph_cache)
            if graph is None:
                continue

            for cross_reference in graph.get_chunk_cross_references(
                anchor_chunk.chunk_id
            ):
                target_chunk_id = cross_reference.target_chunk_id
                if target_chunk_id is None or target_chunk_id in present_chunk_ids:
                    continue

                target_document_chunk = graph.chunks.get(target_chunk_id)
                if target_document_chunk is None:
                    continue

                present_chunk_ids.add(target_chunk_id)
                added_chunks.append(
                    to_retrieved_chunk(
                        document_chunk=target_document_chunk,
                        anchor_chunk=anchor_chunk,
                        relation=_REFERENCED_PROCEDURE_RELATION,
                        distance=_REFERENCED_PROCEDURE_DISTANCE,
                        query_intent=query_intent,
                    )
                )

        return [*chunks, *added_chunks]

    def _graph_for_document(
        self,
        document_id: str,
        graph_cache: dict[str, DocumentGraph | None],
    ) -> DocumentGraph | None:
        if document_id not in graph_cache:
            graph_cache[document_id] = self.document_lookup_service.get_document_graph(
                document_id
            )
        return graph_cache[document_id]


__all__ = ["CrossReferenceContextExpander"]
