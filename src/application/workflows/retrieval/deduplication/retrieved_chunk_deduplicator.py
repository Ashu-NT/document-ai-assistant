from src.application.workflows.retrieval.deduplication.duplicate_group import (
    DuplicateGroup,
)
from src.application.workflows.retrieval.deduplication.retrieval_deduplication_policy import (
    RetrievalDeduplicationPolicy,
)
from src.application.workflows.retrieval.deduplication.retrieval_deduplication_result import (
    RetrievalDeduplicationResult,
)
from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    RetrievedChunkSignature,
    extract_identifier_tokens,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class RetrievedChunkDeduplicator:
    def __init__(
        self,
        *,
        deduplication_policy: RetrievalDeduplicationPolicy | None = None,
    ) -> None:
        self.deduplication_policy = (
            deduplication_policy or RetrievalDeduplicationPolicy()
        )

    def deduplicate(
        self,
        *,
        query: RetrievalQuery | None,
        chunks: list[RetrievedChunk],
    ) -> RetrievalDeduplicationResult:
        query_identifiers = self._query_identifiers(query)
        groups: list[dict[str, object]] = []

        for chunk in chunks:
            signature = RetrievedChunkSignature.from_chunk(chunk)
            matched_group: dict[str, object] | None = None
            matched_reason: str | None = None

            for group in groups:
                reason = self.deduplication_policy.duplicate_reason(
                    left_chunk=group["representative"],
                    left_signature=group["signature"],
                    right_chunk=chunk,
                    right_signature=signature,
                )
                if reason is None:
                    continue
                matched_group = group
                matched_reason = reason
                break

            if matched_group is None:
                groups.append(
                    {
                        "representative": chunk,
                        "signature": signature,
                        "collapsed": [],
                        "reason": None,
                        "selection_reason": "unique_candidate",
                    }
                )
                continue

            representative = matched_group["representative"]
            representative_signature = matched_group["signature"]
            if self._is_better_representative(
                query_identifiers=query_identifiers,
                candidate=chunk,
                candidate_signature=signature,
                existing=representative,
                existing_signature=representative_signature,
            ):
                matched_group["collapsed"].append(representative)
                matched_group["representative"] = chunk
                matched_group["signature"] = signature
                matched_group["selection_reason"] = (
                    self._representative_selection_reason(
                        query_identifiers=query_identifiers,
                        winner=chunk,
                        winner_signature=signature,
                        loser=representative,
                        loser_signature=representative_signature,
                    )
                )
            else:
                matched_group["collapsed"].append(chunk)
                matched_group["selection_reason"] = (
                    self._representative_selection_reason(
                        query_identifiers=query_identifiers,
                        winner=representative,
                        winner_signature=representative_signature,
                        loser=chunk,
                        loser_signature=signature,
                    )
                )

            matched_group["reason"] = matched_reason

        duplicate_groups = [
            self._to_duplicate_group(group)
            for group in groups
        ]
        representatives = sorted(
            (
                group.representative
                for group in duplicate_groups
            ),
            key=lambda chunk: (
                -chunk.score,
                self._coerce_int(chunk.metadata.get("sequence_number")) or 10**6,
                chunk.source.page_start or chunk.source.page_end or 10**6,
            ),
        )
        return RetrievalDeduplicationResult(
            chunks=representatives,
            groups=duplicate_groups,
        )

    def _is_better_representative(
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

    def _representative_selection_reason(
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
        return RetrievedChunkDeduplicator._metadata_score(
            chunk,
            "sql_keyword_source_score",
        )

    @staticmethod
    def _dense_score(chunk: RetrievedChunk) -> float:
        return RetrievedChunkDeduplicator._metadata_score(
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

    def _to_duplicate_group(
        self,
        group: dict[str, object],
    ) -> DuplicateGroup:
        representative = group["representative"]
        collapsed = group["collapsed"]
        enriched_representative = self._with_group_metadata(
            representative,
            collapsed_chunks=collapsed,
            reason=group["reason"],
            selection_reason=group["selection_reason"],
        )
        return DuplicateGroup(
            representative=enriched_representative,
            collapsed_chunks=list(collapsed),
            reason=group["reason"],
            representative_selection_reason=group["selection_reason"],
        )

    @staticmethod
    def _with_group_metadata(
        chunk: RetrievedChunk,
        *,
        collapsed_chunks: list[RetrievedChunk],
        reason: str | None,
        selection_reason: str | None,
    ) -> RetrievedChunk:
        metadata = dict(chunk.metadata)
        if collapsed_chunks:
            metadata["dedup_collapsed_chunk_ids"] = ",".join(
                collapsed_chunk.chunk_id
                for collapsed_chunk in collapsed_chunks
            )
            metadata["dedup_group_size"] = str(1 + len(collapsed_chunks))
            metadata["dedup_reason"] = str(reason or "")
            metadata["dedup_representative_selection_reason"] = str(
                selection_reason or ""
            )

        return RetrievedChunk(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            content=chunk.content,
            score=chunk.score,
            retrieval_source=chunk.retrieval_source,
            chunk_type=chunk.chunk_type,
            section_id=chunk.section_id,
            section_path=list(chunk.section_path),
            source=chunk.source,
            citation=chunk.citation,
            metadata=metadata,
        )

    @staticmethod
    def _query_identifiers(query: RetrievalQuery | None) -> set[str]:
        if query is None:
            return set()

        identifiers = set(extract_identifier_tokens(query.effective_query()))
        identifiers.update(
            token.lower()
            for token in query.detected_identifiers
            if token and token.strip()
        )
        return identifiers

    @staticmethod
    def _coerce_int(value: object) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None
