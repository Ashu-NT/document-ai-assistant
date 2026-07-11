from __future__ import annotations

from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    RetrievedChunkSignature,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievedChunk


class DuplicateRepresentativeSelector:
    """Picks which chunk in a duplicate group becomes the representative."""

    def is_better_representative(
        self,
        *,
        query_identifiers: set[str],
        candidate: RetrievedChunk,
        candidate_signature: RetrievedChunkSignature,
        existing: RetrievedChunk,
        existing_signature: RetrievedChunkSignature,
    ) -> bool:
        return self._representative_sort_key(
            chunk=candidate,
            signature=candidate_signature,
            query_identifiers=query_identifiers,
        ) < self._representative_sort_key(
            chunk=existing,
            signature=existing_signature,
            query_identifiers=query_identifiers,
        )

    def representative_selection_reason(
        self,
        *,
        query_identifiers: set[str],
        winner: RetrievedChunk,
        winner_signature: RetrievedChunkSignature,
        loser: RetrievedChunk,
        loser_signature: RetrievedChunkSignature,
    ) -> str:
        comparisons = (
            (
                "role_priority",
                self._category_rank(winner, winner_signature),
                self._category_rank(loser, loser_signature),
            ),
            ("final_retrieval_score", winner.score, loser.score),
            (
                "exact_query_identifier_match",
                self._identifier_match_count(winner_signature, query_identifiers),
                self._identifier_match_count(loser_signature, query_identifiers),
            ),
            ("keyword_score", self._keyword_score(winner), self._keyword_score(loser)),
            ("dense_score", self._dense_score(winner), self._dense_score(loser)),
            (
                "focused_length",
                len(winner_signature.stripped_token_set),
                len(loser_signature.stripped_token_set),
            ),
            (
                "page_order",
                winner.source.page_start or winner.source.page_end or 10**6,
                loser.source.page_start or loser.source.page_end or 10**6,
            ),
            (
                "sequence_order",
                winner_signature.sequence_number,
                loser_signature.sequence_number,
            ),
        )
        for label, winner_value, loser_value in comparisons:
            if winner_value != loser_value:
                return label
        return "stable_order"

    def _representative_sort_key(
        self,
        *,
        chunk: RetrievedChunk,
        signature: RetrievedChunkSignature,
        query_identifiers: set[str],
    ) -> tuple[object, ...]:
        return (
            self._category_rank(chunk, signature),
            -chunk.score,
            -self._identifier_match_count(signature, query_identifiers),
            -self._keyword_score(chunk),
            -self._dense_score(chunk),
            len(signature.stripped_token_set),
            chunk.source.page_start or chunk.source.page_end or 10**6,
            signature.sequence_number,
        )

    @staticmethod
    def _category_rank(
        chunk: RetrievedChunk,
        signature: RetrievedChunkSignature,
    ) -> int:
        if signature.role == "context_companion":
            return 4
        if signature.role == "overview_companion":
            return 5
        if signature.role == "asset_companion":
            return 6
        if chunk.chunk_type == ChunkType.SPARE_PARTS_TABLE or signature.is_table_like:
            return 2
        if chunk.chunk_type in {
            ChunkType.SAFETY_WARNING,
            ChunkType.MAINTENANCE_PROCEDURE,
            ChunkType.MAINTENANCE_INTERVAL,
            ChunkType.TROUBLESHOOTING,
            ChunkType.TECHNICAL_SPECIFICATION,
            ChunkType.INSTALLATION_INSTRUCTION,
            ChunkType.OPERATION_INSTRUCTION,
        }:
            return 3
        return 1

    @staticmethod
    def _identifier_match_count(
        signature: RetrievedChunkSignature,
        query_identifiers: set[str],
    ) -> int:
        if not query_identifiers:
            return 0
        return len(signature.identifier_tokens & query_identifiers)

    @staticmethod
    def _keyword_score(chunk: RetrievedChunk) -> float:
        return DuplicateRepresentativeSelector._metadata_score(
            chunk,
            "sql_keyword_source_score",
        )

    @staticmethod
    def _dense_score(chunk: RetrievedChunk) -> float:
        return DuplicateRepresentativeSelector._metadata_score(
            chunk,
            "dense_source_score",
        )

    @staticmethod
    def _metadata_score(chunk: RetrievedChunk, key: str) -> float:
        raw_value = chunk.metadata.get(key)
        if raw_value is None:
            return 0.0

        try:
            return float(raw_value)
        except (TypeError, ValueError):
            return 0.0
