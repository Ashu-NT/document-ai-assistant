from __future__ import annotations

from src.application.workflows.retrieval.deduplication.duplicate_group import (
    DuplicateGroup,
)
from src.application.workflows.retrieval.deduplication.duplicate_representative_selector import (
    DuplicateRepresentativeSelector,
)
from src.application.workflows.retrieval.deduplication.retrieval_deduplication_policy import (
    RetrievalDeduplicationPolicy,
)
from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    RetrievedChunkSignature,
)
from src.domain.retrieval import RetrievedChunk


class DuplicateGroupBuilder:
    """Runs the pairwise duplicate-matching loop and assembles the resulting
    DuplicateGroup objects, including the representative's merged metadata."""

    def __init__(
        self,
        *,
        deduplication_policy: RetrievalDeduplicationPolicy,
        representative_selector: DuplicateRepresentativeSelector,
    ) -> None:
        self.deduplication_policy = deduplication_policy
        self.representative_selector = representative_selector

    def group_document_chunks(
        self,
        indexed_chunks: list[tuple[int, RetrievedChunk]],
        *,
        query_identifiers: set[str],
    ) -> list[dict[str, object]]:
        """Runs the pairwise duplicate-matching loop over chunks already
        known to belong to the same document. Extracted so deduplicate()
        can call it once per document bucket instead of once globally."""
        groups: list[dict[str, object]] = []

        for index, chunk in indexed_chunks:
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
                        "first_seen_index": index,
                    }
                )
                continue

            representative = matched_group["representative"]
            representative_signature = matched_group["signature"]
            if self.representative_selector.is_better_representative(
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
                    self.representative_selector.representative_selection_reason(
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
                    self.representative_selector.representative_selection_reason(
                        query_identifiers=query_identifiers,
                        winner=representative,
                        winner_signature=representative_signature,
                        loser=chunk,
                        loser_signature=signature,
                    )
                )

            matched_group["reason"] = matched_reason

        return groups

    def to_duplicate_group(
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
            statistics=chunk.statistics,
            metadata=metadata,
            identifier_values=list(chunk.identifier_values),
        )
