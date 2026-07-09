from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.document.value_objects import ChunkStatistics


@dataclass(slots=True)
class AnswerSource:
    source_number: int
    chunk_id: str
    chunk_name: str | None = None
    chunk_type: str | None = None
    document_id: str | None = None
    document_title: str | None = None
    section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    score: float | None = None
    content: str = ""
    table_rows: list[list[str]] | None = None
    # Carried straight from the source RetrievedChunk (plan section 9.1) so
    # answer formatting doesn't have to re-derive signal that already
    # existed upstream -- see 4.1.
    retrieval_source: str | None = None
    section_id: str | None = None
    statistics: "ChunkStatistics | None" = None
    identifier_values: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    # Derived from metadata["dedup_collapsed_chunk_ids"] (set by
    # RetrievedChunkDeduplicator) -- the closest existing equivalent to a
    # split-chunk "family" reference: the chunk_ids of sibling chunks that
    # were collapsed into this one as duplicates during retrieval.
    # table_ids/picture_ids/chunk_index/chunk_total from the original
    # DocumentChunk are NOT included here: RetrievedChunk (this class's only
    # input) carries none of those as real fields, and nothing threads them
    # into its metadata dict today either -- surfacing them here would mean
    # a field that's always empty. Doing so would require first enriching
    # RetrievedChunk itself, a retrieval-layer change out of scope for this
    # answer-context plan.
    collapsed_chunk_ids: list[str] = field(default_factory=list)
