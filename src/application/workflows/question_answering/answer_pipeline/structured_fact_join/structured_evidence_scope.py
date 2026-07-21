from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Iterable

from src.domain.retrieval import RetrievedChunk


@dataclass(frozen=True, slots=True)
class StructuredEvidenceScope:
    document_ids: frozenset[str]
    chunk_ids: frozenset[str]
    table_ids: frozenset[str]
    page_numbers: frozenset[int]

    @classmethod
    def from_chunks(
        cls,
        chunks: Iterable[RetrievedChunk],
    ) -> "StructuredEvidenceScope":
        document_ids: set[str] = set()
        chunk_ids: set[str] = set()
        table_ids: set[str] = set()
        page_numbers: set[int] = set()

        for chunk in chunks:
            if chunk.document_id:
                document_ids.add(chunk.document_id)
            if chunk.chunk_id:
                chunk_ids.add(chunk.chunk_id)
            chunk_ids.update(_collapsed_chunk_ids(chunk))
            table_ids.update(_table_ids(chunk))
            page_numbers.update(_page_numbers(chunk))

        return cls(
            document_ids=frozenset(document_ids),
            chunk_ids=frozenset(chunk_ids),
            table_ids=frozenset(table_ids),
            page_numbers=frozenset(page_numbers),
        )

    def contains_chunk_id(self, chunk_id: str | None) -> bool:
        normalized = str(chunk_id or "").strip()
        return bool(normalized) and normalized in self.chunk_ids

    def contains_table_id(self, table_id: str | None) -> bool:
        normalized = str(table_id or "").strip()
        return bool(normalized) and normalized in self.table_ids

    def overlaps_pages(
        self,
        *,
        page_start: int | None,
        page_end: int | None,
    ) -> bool:
        if page_start is None:
            return False
        last_page = page_end if page_end is not None and page_end >= page_start else page_start
        return any(page in self.page_numbers for page in range(page_start, last_page + 1))


def _collapsed_chunk_ids(chunk: RetrievedChunk) -> set[str]:
    raw_value = str(chunk.metadata.get("dedup_collapsed_chunk_ids", "") or "").strip()
    if not raw_value:
        return set()
    return {
        chunk_id.strip()
        for chunk_id in raw_value.split(",")
        if chunk_id.strip()
    }


def _table_ids(chunk: RetrievedChunk) -> set[str]:
    table_ids: set[str] = set()
    for key in ("hydrated_table_ids", "table_id", "table_ids"):
        raw_value = str(chunk.metadata.get(key, "") or "").strip()
        if not raw_value:
            continue
        if raw_value.startswith("[") and raw_value.endswith("]"):
            try:
                parsed = json.loads(raw_value)
            except json.JSONDecodeError:
                parsed = []
            if isinstance(parsed, list):
                table_ids.update(
                    str(value).strip() for value in parsed if str(value).strip()
                )
            continue
        table_ids.update(
            value.strip() for value in raw_value.split(",") if value.strip()
        )
    return table_ids


def _page_numbers(chunk: RetrievedChunk) -> set[int]:
    source = chunk.source
    if source.page_start is None:
        return set()
    last_page = (
        source.page_end
        if source.page_end is not None and source.page_end >= source.page_start
        else source.page_start
    )
    return set(range(source.page_start, last_page + 1))
