from src.application.services.document import DocumentLookupService
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
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class RetrievalContextExpander:
    def __init__(
        self,
        document_lookup_service: DocumentLookupService,
        *,
        neighbor_window: int = 1,
        max_context_chunks: int = 8,
        query_intent_inferer: RetrievalQueryIntentInferer | None = None,
        context_assembler: RetrievalContextAssembler | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.neighbor_window = max(0, neighbor_window)
        self.max_context_chunks = max(1, max_context_chunks)
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

        query_intent = self.query_intent_inferer.infer(query)
        chunk_cache: dict[str, list] = {}
        candidates_by_anchor_id: dict[str, list[RetrievalContextCandidate]] = {}

        for anchor_chunk in chunks:
            document_chunks = chunk_cache.get(anchor_chunk.document_id)
            if document_chunks is None:
                document_chunks = self.document_lookup_service.list_chunks_by_document(
                    anchor_chunk.document_id
                )
                chunk_cache[anchor_chunk.document_id] = document_chunks

            chunk_by_id = {
                document_chunk.chunk_id: document_chunk
                for document_chunk in document_chunks
            }
            anchor_document_chunk = chunk_by_id.get(anchor_chunk.chunk_id)
            if anchor_document_chunk is None:
                continue

            candidates_by_anchor_id[anchor_chunk.chunk_id] = (
                self._select_context_chunks(
                    anchor_chunk=anchor_chunk,
                    document_chunks=document_chunks,
                    anchor_document_chunk=anchor_document_chunk,
                    query_intent=query_intent,
                )
            )

        return self.context_assembler.assemble(
            anchors=list(chunks),
            candidates_by_anchor_id=candidates_by_anchor_id,
            max_context_chunks=self.max_context_chunks,
            query_intent=query_intent,
            to_retrieved_chunk=lambda candidate: self._to_retrieved_chunk(
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
        document_chunks: list,
        anchor_document_chunk,
        query_intent: RetrievalQueryIntent,
    ) -> list[RetrievalContextCandidate]:
        candidates_by_chunk_id: dict[str, RetrievalContextCandidate] = {}

        for document_chunk in document_chunks:
            if document_chunk.chunk_id == anchor_document_chunk.chunk_id:
                continue

            relation, distance = self._context_relation(
                anchor_document_chunk=anchor_document_chunk,
                document_chunk=document_chunk,
            )
            if relation is None:
                continue

            candidate = RetrievalContextCandidate(
                anchor_chunk=anchor_chunk,
                document_chunk=document_chunk,
                relation=relation,
                distance=distance,
                priority=self._context_priority(
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

    def _context_relation(
        self,
        *,
        anchor_document_chunk,
        document_chunk,
    ) -> tuple[str | None, int]:
        distance = abs(
            document_chunk.sequence_number - anchor_document_chunk.sequence_number
        )

        if self._shares_chunk_family(anchor_document_chunk, document_chunk):
            return "same_section_part", max(1, distance)
        if self._is_ancestor_overview(anchor_document_chunk, document_chunk):
            return "ancestor_overview", max(1, distance)
        if self._shares_assets(anchor_document_chunk, document_chunk):
            return "asset_companion", max(1, distance)
        if self._is_descendant_detail(anchor_document_chunk, document_chunk):
            return "descendant_detail", max(1, distance)
        if self._is_same_parent_path(anchor_document_chunk, document_chunk):
            return "sibling_section", max(1, distance)
        if 0 < distance <= self.neighbor_window:
            return "neighbor", distance

        return None, distance

    @staticmethod
    def _shares_chunk_family(anchor_document_chunk, document_chunk) -> bool:
        return (
            anchor_document_chunk.section_id is not None
            and anchor_document_chunk.section_id == document_chunk.section_id
            and max(
                anchor_document_chunk.chunk_total,
                document_chunk.chunk_total,
            ) > 1
        )

    @staticmethod
    def _shares_assets(anchor_document_chunk, document_chunk) -> bool:
        return bool(
            set(anchor_document_chunk.table_ids) & set(document_chunk.table_ids)
            or set(anchor_document_chunk.picture_ids) & set(document_chunk.picture_ids)
        )

    @staticmethod
    def _is_ancestor_overview(anchor_document_chunk, document_chunk) -> bool:
        return (
            document_chunk.chunk_type == ChunkType.OVERVIEW
            and RetrievalContextExpander._is_path_prefix(
                document_chunk.section_path,
                anchor_document_chunk.section_path,
            )
            and document_chunk.section_path != anchor_document_chunk.section_path
        )

    @staticmethod
    def _is_descendant_detail(anchor_document_chunk, document_chunk) -> bool:
        return (
            anchor_document_chunk.chunk_type == ChunkType.OVERVIEW
            and document_chunk.chunk_type != ChunkType.OVERVIEW
            and RetrievalContextExpander._is_path_prefix(
                anchor_document_chunk.section_path,
                document_chunk.section_path,
            )
            and anchor_document_chunk.section_path != document_chunk.section_path
        )

    @staticmethod
    def _is_same_parent_path(anchor_document_chunk, document_chunk) -> bool:
        if len(anchor_document_chunk.section_path) <= 1:
            return False
        if len(anchor_document_chunk.section_path) != len(document_chunk.section_path):
            return False
        return (
            anchor_document_chunk.section_path[:-1]
            == document_chunk.section_path[:-1]
            and anchor_document_chunk.section_path[-1]
            != document_chunk.section_path[-1]
        )

    @staticmethod
    def _is_path_prefix(
        candidate_ancestor_path: list[str],
        candidate_descendant_path: list[str],
    ) -> bool:
        if not candidate_ancestor_path:
            return False
        if len(candidate_ancestor_path) > len(candidate_descendant_path):
            return False
        return (
            candidate_descendant_path[: len(candidate_ancestor_path)]
            == candidate_ancestor_path
        )

    @staticmethod
    def _context_priority(
        *,
        relation: str,
        query_intent: RetrievalQueryIntent,
        document_chunk,
    ) -> int:
        relation_priority = {
            "same_section_part": 100,
            "ancestor_overview": 94,
            "descendant_detail": 92,
            "asset_companion": 90,
            "sibling_section": 70,
            "neighbor": 60,
        }
        priority = relation_priority.get(relation, 50)

        if query_intent in {
            RetrievalQueryIntent.TABLE,
            RetrievalQueryIntent.FIGURE,
            RetrievalQueryIntent.SPECIFICATION,
        }:
            if relation == "asset_companion":
                priority += 20
            if document_chunk.chunk_type in {
                ChunkType.SPARE_PARTS_TABLE,
                ChunkType.DRAWING_REFERENCE,
                ChunkType.TECHNICAL_SPECIFICATION,
            }:
                priority += 10

        if query_intent == RetrievalQueryIntent.OVERVIEW:
            if relation == "same_section_part":
                priority += 8
            if relation == "ancestor_overview":
                priority += 20
            if relation == "descendant_detail":
                priority += 10

        if query_intent in {
            RetrievalQueryIntent.PROCEDURE,
            RetrievalQueryIntent.TROUBLESHOOTING,
            RetrievalQueryIntent.SAFETY,
        }:
            if relation == "same_section_part":
                priority += 15
            if relation in {"ancestor_overview", "descendant_detail"}:
                priority += 12
            if relation == "sibling_section":
                priority += 8

        return priority

    @staticmethod
    def _to_retrieved_chunk(
        *,
        document_chunk,
        anchor_chunk: RetrievedChunk,
        relation: str,
        distance: int,
        query_intent: RetrievalQueryIntent,
    ) -> RetrievedChunk:
        metadata = {
            "anchor_chunk_id": anchor_chunk.chunk_id,
            "context_distance": str(distance),
            "context_relation": relation,
            "query_intent": query_intent.value,
        }

        return RetrievedChunk(
            chunk_id=document_chunk.chunk_id,
            document_id=document_chunk.document_id,
            content=document_chunk.content,
            score=max(anchor_chunk.score - (distance * 0.01), 0.0),
            retrieval_source="context_expansion",
            chunk_type=document_chunk.chunk_type,
            section_id=document_chunk.section_id,
            section_path=list(document_chunk.section_path),
            source=document_chunk.source,
            metadata=metadata,
        )
