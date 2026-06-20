from src.application.services.document import DocumentLookupService
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery
from src.domain.retrieval import RetrievedChunk


class RetrievalContextExpander:
    def __init__(
        self,
        document_lookup_service: DocumentLookupService,
        *,
        neighbor_window: int = 1,
        max_context_chunks: int = 8,
        query_intent_inferer: RetrievalQueryIntentInferer | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.neighbor_window = max(0, neighbor_window)
        self.max_context_chunks = max(1, max_context_chunks)
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

        query_intent = self.query_intent_inferer.infer(query)
        expanded: list[RetrievedChunk] = []
        seen: set[str] = set()
        chunk_cache: dict[str, list] = {}
        max_result_count = max(len(chunks), self.max_context_chunks)

        for chunk in chunks:
            self._append_chunk(expanded, seen, chunk)
            if len(expanded) >= max_result_count:
                break

            document_chunks = chunk_cache.get(chunk.document_id)
            if document_chunks is None:
                document_chunks = self.document_lookup_service.list_chunks_by_document(
                    chunk.document_id
                )
                chunk_cache[chunk.document_id] = document_chunks

            chunk_by_id = {
                document_chunk.chunk_id: document_chunk
                for document_chunk in document_chunks
            }
            anchor_document_chunk = chunk_by_id.get(chunk.chunk_id)
            if anchor_document_chunk is None:
                continue

            for document_chunk, relation, distance in self._select_context_chunks(
                document_chunks=document_chunks,
                anchor_document_chunk=anchor_document_chunk,
                query_intent=query_intent,
            ):
                self._append_chunk(
                    expanded,
                    seen,
                    self._to_retrieved_chunk(
                        document_chunk=document_chunk,
                        anchor_chunk=chunk,
                        relation=relation,
                        distance=distance,
                        query_intent=query_intent,
                    ),
                )
                if len(expanded) >= max_result_count:
                    break

            if len(expanded) >= max_result_count:
                break

        return expanded

    def _select_context_chunks(
        self,
        *,
        document_chunks: list,
        anchor_document_chunk,
        query_intent: RetrievalQueryIntent,
    ) -> list[tuple[object, str, int]]:
        candidates_by_chunk_id: dict[str, tuple[int, int, object, str]] = {}

        for document_chunk in document_chunks:
            if document_chunk.chunk_id == anchor_document_chunk.chunk_id:
                continue

            relation, distance = self._context_relation(
                anchor_document_chunk=anchor_document_chunk,
                document_chunk=document_chunk,
            )
            if relation is None:
                continue

            priority = self._context_priority(
                relation=relation,
                query_intent=query_intent,
                document_chunk=document_chunk,
            )
            existing = candidates_by_chunk_id.get(document_chunk.chunk_id)
            candidate = (priority, distance, document_chunk, relation)
            if existing is None or self._is_better_candidate(candidate, existing):
                candidates_by_chunk_id[document_chunk.chunk_id] = candidate

        ranked_candidates = sorted(
            candidates_by_chunk_id.values(),
            key=lambda item: (-item[0], item[1], item[2].sequence_number),
        )
        return [
            (document_chunk, relation, distance)
            for _, distance, document_chunk, relation in ranked_candidates
        ]

    @staticmethod
    def _is_better_candidate(
        candidate: tuple[int, int, object, str],
        existing: tuple[int, int, object, str],
    ) -> bool:
        if candidate[0] != existing[0]:
            return candidate[0] > existing[0]
        return candidate[1] < existing[1]

    def _context_relation(
        self,
        *,
        anchor_document_chunk,
        document_chunk,
    ) -> tuple[str | None, int]:
        distance = abs(
            document_chunk.sequence_number - anchor_document_chunk.sequence_number
        )

        if self._shares_assets(anchor_document_chunk, document_chunk):
            return "asset_companion", max(1, distance)
        if self._is_ancestor_overview(anchor_document_chunk, document_chunk):
            return "ancestor_overview", max(1, distance)
        if self._is_descendant_detail(anchor_document_chunk, document_chunk):
            return "descendant_detail", max(1, distance)
        if self._shares_chunk_family(anchor_document_chunk, document_chunk):
            return "same_section_part", max(1, distance)
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
            and (
                anchor_document_chunk.chunk_total > 1
                or document_chunk.chunk_total > 1
                or anchor_document_chunk.chunk_type == ChunkType.OVERVIEW
                or document_chunk.chunk_type == ChunkType.OVERVIEW
            )
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
            "asset_companion": 95,
            "ancestor_overview": 90,
            "descendant_detail": 88,
            "same_section_part": 84,
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
            if relation == "ancestor_overview":
                priority += 15
            if relation == "descendant_detail":
                priority += 10

        if query_intent in {
            RetrievalQueryIntent.PROCEDURE,
            RetrievalQueryIntent.TROUBLESHOOTING,
            RetrievalQueryIntent.SAFETY,
        }:
            if relation in {"same_section_part", "sibling_section", "ancestor_overview"}:
                priority += 12

        return priority

    @staticmethod
    def _append_chunk(
        expanded: list[RetrievedChunk],
        seen: set[str],
        chunk: RetrievedChunk,
    ) -> None:
        if chunk.chunk_id in seen:
            return

        seen.add(chunk.chunk_id)
        expanded.append(chunk)

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
