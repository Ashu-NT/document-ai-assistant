from src.application.contracts.retrieval import Reranker
from src.application.workflows.retrieval import RetrievalQueryIntent
from src.application.workflows.retrieval import RetrievalQueryIntentInferer
from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    detect_chunk_role,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery, RetrievedChunk
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import (
    extract_query_terms,
    normalize_query_text,
)

_IDENTIFIER_FIT_TYPES = {
    ChunkType.SPARE_PARTS_TABLE,
    ChunkType.TECHNICAL_SPECIFICATION,
    ChunkType.CERTIFICATION_INFO,
    ChunkType.DRAWING_REFERENCE,
}
_NOISE_PATH_MARKERS = (
    "revision / modification table",
    "table of contents",
    "environmentally",
    "responsible solutions",
    "engineered",
)


class DeterministicHybridReranker(Reranker):
    def __init__(
        self,
        *,
        intent_inferer: RetrievalQueryIntentInferer | None = None,
    ) -> None:
        self.intent_inferer = intent_inferer or RetrievalQueryIntentInferer()

    def rerank(
        self,
        query: RetrievalQuery,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        intent = self.intent_inferer.infer(query)
        query_terms = extract_query_terms(query.effective_query())
        query_identifiers = {
            identifier.lower()
            for identifier in query.detected_identifiers
            if identifier and identifier.strip()
        }
        return sorted(
            chunks,
            key=lambda chunk: self._score_chunk(
                query=query,
                chunk=chunk,
                intent=intent,
                query_terms=query_terms,
                query_identifiers=query_identifiers,
            ),
            reverse=True,
        )

    def _score_chunk(
        self,
        *,
        query: RetrievalQuery,
        chunk: RetrievedChunk,
        intent: RetrievalQueryIntent,
        query_terms: list[str],
        query_identifiers: set[str],
    ) -> tuple[float, float, int, int]:
        sql_score = self._metadata_float(chunk, "sql_keyword_source_score")
        dense_score = self._metadata_float(chunk, "dense_source_score")
        best_score = self._metadata_float(chunk, "best_source_score", default=chunk.score)
        identifier_matches = max(
            self._metadata_int(chunk, "sql_exact_identifier_matches"),
            self._identifier_match_count(chunk, query_identifiers),
        )
        role = detect_chunk_role(chunk.content)
        section_hit_count = self._section_path_hit_count(chunk, query_terms)

        score = chunk.score * 8.0
        score += best_score * 4.0
        score += sql_score * 3.0
        score += dense_score * 1.25
        score += identifier_matches * 35.0
        score += self._role_score(role)
        score += self._intent_chunk_type_score(intent, chunk.chunk_type, query)
        score += float(section_hit_count) * 2.5
        score -= self._noise_penalty(chunk)

        return (
            score,
            -float(chunk.source.page_start or chunk.source.page_end or 10**6),
            -self._metadata_int(chunk, "sequence_number"),
            -len(chunk.content or ""),
        )

    @staticmethod
    def _metadata_float(
        chunk: RetrievedChunk,
        key: str,
        *,
        default: float = 0.0,
    ) -> float:
        raw_value = chunk.metadata.get(key)
        if raw_value is None:
            return default
        try:
            return float(raw_value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _metadata_int(
        chunk: RetrievedChunk,
        key: str,
        *,
        default: int = 0,
    ) -> int:
        raw_value = chunk.metadata.get(key)
        if raw_value is None:
            return default
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _identifier_match_count(
        chunk: RetrievedChunk,
        query_identifiers: set[str],
    ) -> int:
        if not query_identifiers:
            return 0
        lowered_content = chunk.content.lower()
        return sum(1 for identifier in query_identifiers if identifier in lowered_content)

    @staticmethod
    def _role_score(role: str) -> float:
        return {
            "atomic_evidence": 14.0,
            "asset_companion": 6.0,
            "context_companion": 2.0,
            "overview_companion": -6.0,
        }.get(role, 0.0)

    @staticmethod
    def _section_path_hit_count(
        chunk: RetrievedChunk,
        query_terms: list[str],
    ) -> int:
        normalized_path = normalize_query_text(chunk.section_path_text())
        return sum(1 for term in query_terms if term in normalized_path)

    def _intent_chunk_type_score(
        self,
        intent: RetrievalQueryIntent,
        chunk_type: ChunkType,
        query: RetrievalQuery,
    ) -> float:
        if query.chunk_types and chunk_type in query.chunk_types:
            base = 8.0
        else:
            base = 0.0

        if intent == RetrievalQueryIntent.IDENTIFIER:
            if chunk_type in _IDENTIFIER_FIT_TYPES:
                return base + 14.0
            if chunk_type == ChunkType.OVERVIEW:
                return base - 8.0
            if chunk_type == ChunkType.GENERAL:
                return base + 2.0
        if intent == RetrievalQueryIntent.TABLE:
            if chunk_type == ChunkType.SPARE_PARTS_TABLE:
                return base + 15.0
            if chunk_type in {ChunkType.TECHNICAL_SPECIFICATION, ChunkType.CERTIFICATION_INFO}:
                return base + 10.0
        if intent == RetrievalQueryIntent.SPECIFICATION:
            if chunk_type in {ChunkType.TECHNICAL_SPECIFICATION, ChunkType.CERTIFICATION_INFO}:
                return base + 15.0
            if chunk_type == ChunkType.SPARE_PARTS_TABLE:
                return base + 8.0
            if chunk_type == ChunkType.OVERVIEW:
                return base - 4.0
        if intent == RetrievalQueryIntent.PROCEDURE:
            if chunk_type == ChunkType.OPERATION_INSTRUCTION:
                return base + 16.0
            if chunk_type == ChunkType.MAINTENANCE_PROCEDURE:
                return base + 15.0
            if chunk_type == ChunkType.MAINTENANCE_INTERVAL:
                return base + 12.0
            if chunk_type == ChunkType.TROUBLESHOOTING:
                return base + 9.0
            if chunk_type == ChunkType.OVERVIEW:
                return base - 8.0
            if chunk_type == ChunkType.GENERAL:
                return base + 1.0
        if intent == RetrievalQueryIntent.TROUBLESHOOTING:
            if chunk_type == ChunkType.TROUBLESHOOTING:
                return base + 16.0
            if chunk_type == ChunkType.OPERATION_INSTRUCTION:
                return base + 7.0
        if intent == RetrievalQueryIntent.SAFETY:
            if chunk_type == ChunkType.SAFETY_WARNING:
                return base + 14.0
            if chunk_type == ChunkType.OVERVIEW:
                return base - 4.0
        if intent == RetrievalQueryIntent.FIGURE:
            if chunk_type == ChunkType.DRAWING_REFERENCE:
                return base + 16.0
        if intent == RetrievalQueryIntent.OVERVIEW:
            if chunk_type == ChunkType.OVERVIEW:
                return base + 8.0

        return base

    @staticmethod
    def _noise_penalty(chunk: RetrievedChunk) -> float:
        normalized_path = normalize_query_text(chunk.section_path_text())
        penalty = 0.0
        if any(marker in normalized_path for marker in _NOISE_PATH_MARKERS):
            penalty += 8.0
        return penalty
