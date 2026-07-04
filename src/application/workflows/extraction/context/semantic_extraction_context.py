from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.document import DocumentChunk, DocumentSection
from src.domain.extraction import SemanticSourceMetadata


@dataclass(frozen=True, slots=True)
class SemanticExtractionContext:
    """
    A chunk's resolved position in the DocumentGraph, answering:
    - Where is this chunk in the document graph? (chunk, section, page)
    - What section/page/table does it belong to?
    - What nearby context (sibling chunks) can help extraction?
    - What metadata should be attached to entities extracted from it?

    Built once per document by SemanticExtractionContextBuilder and shared
    by two consumers: ExtractionCandidateSelector (deciding which semantic
    entity types are worth asking the LLM for) and ExtractionWorkflow's
    SemanticSourceMetadata construction (deterministic provenance attached
    to extracted entities after the LLM response is parsed — the LLM never
    sees this object).
    """

    document_id: str
    chunk: DocumentChunk

    section: DocumentSection | None = None
    nearby_chunk_ids: tuple[str, ...] = field(default_factory=tuple)

    @property
    def chunk_id(self) -> str:
        return self.chunk.chunk_id

    @property
    def section_id(self) -> str | None:
        return self.chunk.section_id

    @property
    def section_path(self) -> tuple[str, ...]:
        return tuple(self.chunk.section_path)

    @property
    def parent_section_id(self) -> str | None:
        return self.section.parent_section_id if self.section is not None else None

    @property
    def page_start(self) -> int | None:
        return self.chunk.source.page_start

    @property
    def page_end(self) -> int | None:
        return self.chunk.source.page_end

    @property
    def table_id(self) -> str | None:
        return self.chunk.table_ids[0] if self.chunk.table_ids else None

    @property
    def source_element_ids(self) -> tuple[str, ...]:
        return tuple(self.chunk.element_ids)

    def to_source_metadata(self) -> SemanticSourceMetadata:
        return SemanticSourceMetadata(
            document_id=self.document_id,
            chunk_id=self.chunk_id,
            section_id=self.section_id,
            section_path=self.section_path,
            page_start=self.page_start,
            page_end=self.page_end,
            parent_section_id=self.parent_section_id,
            table_id=self.table_id,
            source_element_ids=self.source_element_ids,
            nearby_chunk_ids=self.nearby_chunk_ids,
        )
