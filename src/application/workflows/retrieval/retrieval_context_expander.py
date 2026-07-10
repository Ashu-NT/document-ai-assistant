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
from src.application.workflows.shared.section_path_utils import is_path_prefix
from src.domain.common import ChunkType
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


class _DocumentChunkIndex:
    """Pre-indexes one document's chunk list once so a per-anchor lookup
    only touches chunks that could plausibly match one of
    RetrievalContextExpander's relation types, instead of scanning every
    chunk in the document for every anchor. Each index is a superset lookup
    (it may occasionally include a chunk that _context_relation ultimately
    rejects), never a subset -- the unchanged relation-checking logic is
    still the final word on whether a candidate actually qualifies."""

    def __init__(
        self,
        *,
        by_chunk_id: dict[str, object],
        by_section_id: dict[str, list],
        by_table_id: dict[str, list],
        by_picture_id: dict[str, list],
        overview_by_section_path: dict[tuple, list],
        by_section_path_prefix: dict[tuple, list],
        by_parent_path: dict[tuple, list],
        by_sequence_number: dict[int, list],
    ) -> None:
        self.by_chunk_id = by_chunk_id
        self.by_section_id = by_section_id
        self.by_table_id = by_table_id
        self.by_picture_id = by_picture_id
        self.overview_by_section_path = overview_by_section_path
        self.by_section_path_prefix = by_section_path_prefix
        self.by_parent_path = by_parent_path
        self.by_sequence_number = by_sequence_number

    @classmethod
    def build(cls, document_chunks: list) -> "_DocumentChunkIndex":
        by_chunk_id: dict[str, object] = {}
        by_section_id: dict[str, list] = {}
        by_table_id: dict[str, list] = {}
        by_picture_id: dict[str, list] = {}
        overview_by_section_path: dict[tuple, list] = {}
        by_section_path_prefix: dict[tuple, list] = {}
        by_parent_path: dict[tuple, list] = {}
        by_sequence_number: dict[int, list] = {}

        for chunk in document_chunks:
            by_chunk_id[chunk.chunk_id] = chunk

            if chunk.section_id is not None:
                by_section_id.setdefault(chunk.section_id, []).append(chunk)

            for table_id in chunk.table_ids:
                by_table_id.setdefault(table_id, []).append(chunk)
            for picture_id in chunk.picture_ids:
                by_picture_id.setdefault(picture_id, []).append(chunk)

            path = tuple(chunk.section_path)
            if chunk.chunk_type == ChunkType.OVERVIEW:
                overview_by_section_path.setdefault(path, []).append(chunk)

            # Every proper prefix of this chunk's own path is a bucket it
            # belongs to, for _is_descendant_detail: "chunks whose path
            # starts with the anchor's path" is answered by looking up the
            # anchor's own (exact) path in this index.
            for prefix_length in range(len(path)):
                by_section_path_prefix.setdefault(path[:prefix_length], []).append(chunk)

            if len(path) >= 1:
                by_parent_path.setdefault(path[:-1], []).append(chunk)

            by_sequence_number.setdefault(chunk.sequence_number, []).append(chunk)

        return cls(
            by_chunk_id=by_chunk_id,
            by_section_id=by_section_id,
            by_table_id=by_table_id,
            by_picture_id=by_picture_id,
            overview_by_section_path=overview_by_section_path,
            by_section_path_prefix=by_section_path_prefix,
            by_parent_path=by_parent_path,
            by_sequence_number=by_sequence_number,
        )

    def plausible_candidates(
        self,
        anchor_document_chunk,
        *,
        neighbor_window: int,
    ) -> list:
        candidates: dict[str, object] = {}

        def _add_all(chunks: list) -> None:
            for chunk in chunks:
                candidates[chunk.chunk_id] = chunk

        if anchor_document_chunk.section_id is not None:
            _add_all(self.by_section_id.get(anchor_document_chunk.section_id, []))

        anchor_path = tuple(anchor_document_chunk.section_path)
        for prefix_length in range(len(anchor_path)):
            _add_all(self.overview_by_section_path.get(anchor_path[:prefix_length], []))

        for table_id in anchor_document_chunk.table_ids:
            _add_all(self.by_table_id.get(table_id, []))
        for picture_id in anchor_document_chunk.picture_ids:
            _add_all(self.by_picture_id.get(picture_id, []))

        _add_all(self.by_section_path_prefix.get(anchor_path, []))

        if len(anchor_path) > 1:
            _add_all(self.by_parent_path.get(anchor_path[:-1], []))

        sequence_number = anchor_document_chunk.sequence_number
        for offset in range(-neighbor_window, neighbor_window + 1):
            if offset == 0:
                continue
            _add_all(self.by_sequence_number.get(sequence_number + offset, []))

        return list(candidates.values())


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
        index_cache: dict[str, "_DocumentChunkIndex"] = {}
        candidates_by_anchor_id: dict[str, list[RetrievalContextCandidate]] = {}

        for anchor_chunk in chunks:
            document_chunks = chunk_cache.get(anchor_chunk.document_id)
            if document_chunks is None:
                document_chunks = self.document_lookup_service.list_chunks_by_document(
                    anchor_chunk.document_id
                )
                chunk_cache[anchor_chunk.document_id] = document_chunks
                index_cache[anchor_chunk.document_id] = _DocumentChunkIndex.build(
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
        chunk_index: "_DocumentChunkIndex",
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
            and is_path_prefix(
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
            and is_path_prefix(
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
            statistics=document_chunk.statistics,
            metadata=metadata,
        )
