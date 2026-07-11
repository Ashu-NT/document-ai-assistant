from src.application.workflows.retrieval.deduplication.duplicate_group_builder import (
    DuplicateGroupBuilder,
)
from src.application.workflows.retrieval.deduplication.duplicate_representative_selector import (
    DuplicateRepresentativeSelector,
)
from src.application.workflows.retrieval.deduplication.retrieval_deduplication_policy import (
    RetrievalDeduplicationPolicy,
)
from src.application.workflows.retrieval.deduplication.retrieval_deduplication_result import (
    RetrievalDeduplicationResult,
)
from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    extract_identifier_tokens,
)
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
        self._group_builder = DuplicateGroupBuilder(
            deduplication_policy=self.deduplication_policy,
            representative_selector=DuplicateRepresentativeSelector(),
        )

    def deduplicate(
        self,
        *,
        query: RetrievalQuery | None,
        chunks: list[RetrievedChunk],
    ) -> RetrievalDeduplicationResult:
        query_identifiers = self._query_identifiers(query)

        # duplicate_reason() always returns None for a cross-document pair
        # (see RetrievalDeduplicationPolicy.duplicate_reason's first check),
        # so bucketing by document_id before the pairwise comparison below
        # is behavior-identical -- it only skips comparisons that were
        # already guaranteed to find no match. Cuts the O(n^2) comparison
        # volume down to the sum of per-document group sizes squared,
        # instead of the full candidate pool squared.
        chunks_by_document: dict[str, list[tuple[int, RetrievedChunk]]] = {}
        for index, chunk in enumerate(chunks):
            chunks_by_document.setdefault(chunk.document_id, []).append(
                (index, chunk)
            )

        groups: list[dict[str, object]] = []
        for indexed_chunks in chunks_by_document.values():
            groups.extend(
                self._group_builder.group_document_chunks(
                    indexed_chunks,
                    query_identifiers=query_identifiers,
                )
            )

        # Restore the original chunk order for the returned groups -- each
        # group's position should reflect where its first chunk appeared in
        # the input, not the document-bucketing order used internally.
        groups.sort(key=lambda group: group["first_seen_index"])

        duplicate_groups = [
            self._group_builder.to_duplicate_group(group)
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
