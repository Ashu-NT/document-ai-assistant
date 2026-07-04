from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SemanticSourceMetadata:
    """
    Provenance metadata for extracted semantic entities.

    Links each extracted semantic object back to the document graph, so
    entities (maintenance tasks, intervals, procedures, safety warnings,
    troubleshooting entries, spare parts, equipment, manufacturers) can be
    structurally linked to one another and to their originating section
    during retrieval, not just to a single source chunk.

    Field names mirror the corresponding DocumentGraph/DocumentChunk/
    DocumentSection attributes they are read from:
    - chunk_id, section_id, section_path, page_start, page_end:
      src.domain.document.entities.chunk.DocumentChunk
    - parent_section_id: src.domain.document.entities.section.DocumentSection
    - table_id: src.domain.elements.canonical_element.CanonicalElement.table_id
      (a chunk may reference multiple tables via table_ids; this is the one
      relevant to this entity)
    - source_element_ids: DocumentChunk.element_ids
    - nearby_chunk_ids: sibling chunks under the same section, for
      cross-entity linking (e.g. a troubleshooting entry and the procedure
      it references, chunked separately but under the same section)

    table_row_id has no backing concept yet: TableAsset stores a whole
    table as one markdown blob, and Docling table parsing does not assign
    stable per-row IDs. The field is kept for forward compatibility but is
    never populated until row-level table parsing exists.
    """

    document_id: str
    chunk_id: str

    section_id: str | None = None
    section_path: tuple[str, ...] = field(default_factory=tuple)

    page_start: int | None = None
    page_end: int | None = None

    parent_section_id: str | None = None

    table_id: str | None = None
    table_row_id: str | None = None

    source_element_ids: tuple[str, ...] = field(default_factory=tuple)
    nearby_chunk_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.document_id:
            raise ValueError("SemanticSourceMetadata.document_id is required.")

        if not self.chunk_id:
            raise ValueError("SemanticSourceMetadata.chunk_id is required.")

        if self.page_start is not None and self.page_start < 1:
            raise ValueError("page_start must be >= 1.")

        if self.page_end is not None and self.page_end < 1:
            raise ValueError("page_end must be >= 1.")

        if (
            self.page_start is not None
            and self.page_end is not None
            and self.page_end < self.page_start
        ):
            raise ValueError("page_end cannot be before page_start.")

    @property
    def page_label(self) -> str:
        if self.page_start is None:
            return "-"

        if self.page_end is None or self.page_end == self.page_start:
            return str(self.page_start)

        return f"{self.page_start}-{self.page_end}"

    @property
    def section_label(self) -> str:
        if not self.section_path:
            return "-"

        return " > ".join(self.section_path)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "section_id": self.section_id,
            "section_path": list(self.section_path),
            "page_start": self.page_start,
            "page_end": self.page_end,
            "parent_section_id": self.parent_section_id,
            "table_id": self.table_id,
            "table_row_id": self.table_row_id,
            "source_element_ids": list(self.source_element_ids),
            "nearby_chunk_ids": list(self.nearby_chunk_ids),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SemanticSourceMetadata:
        return cls(
            document_id=str(data["document_id"]),
            chunk_id=str(data["chunk_id"]),
            section_id=data.get("section_id"),
            section_path=tuple(data.get("section_path") or ()),
            page_start=data.get("page_start"),
            page_end=data.get("page_end"),
            parent_section_id=data.get("parent_section_id"),
            table_id=data.get("table_id"),
            table_row_id=data.get("table_row_id") or data.get("row_id"),
            source_element_ids=tuple(data.get("source_element_ids") or ()),
            nearby_chunk_ids=tuple(data.get("nearby_chunk_ids") or ()),
        )
