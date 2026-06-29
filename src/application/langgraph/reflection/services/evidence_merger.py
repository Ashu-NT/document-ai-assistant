from __future__ import annotations

from src.application.langgraph.reflection.policies import RetrievalRetryPolicy
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _page_sort_value(chunk: RetrievedChunk) -> tuple[int, int]:
    page_start = chunk.source.page_start if chunk.source.page_start is not None else 10**9
    page_end = chunk.source.page_end if chunk.source.page_end is not None else page_start
    return (page_start, page_end)


class EvidenceMerger:
    def merge(
        self,
        *,
        initial_chunks: list[RetrievedChunk],
        retry_chunks: list[RetrievedChunk],
        policy: RetrievalRetryPolicy,
        document_id: str | None = None,
    ) -> tuple[list[RetrievedChunk], dict[str, object]]:
        merged: list[RetrievedChunk] = []
        seen_chunk_ids: set[str] = set()
        filtered_wrong_document: list[str] = []

        for chunk in [*initial_chunks, *retry_chunks]:
            if document_id is not None and chunk.document_id != document_id:
                filtered_wrong_document.append(chunk.chunk_id)
                continue
            if policy.deduplicate_by_chunk_id and chunk.chunk_id in seen_chunk_ids:
                continue
            merged.append(chunk)
            seen_chunk_ids.add(chunk.chunk_id)

        merged = sorted(
            merged,
            key=lambda chunk: (-chunk.score, *_page_sort_value(chunk)),
        )[: policy.max_merged_chunks]
        diagnostics = {
            "initial_chunk_count": len(initial_chunks),
            "retry_chunk_count": len(retry_chunks),
            "merged_chunk_count": len(merged),
            "merged_chunk_ids": [chunk.chunk_id for chunk in merged],
            "filtered_wrong_document_chunk_ids": filtered_wrong_document,
        }
        return merged, diagnostics
