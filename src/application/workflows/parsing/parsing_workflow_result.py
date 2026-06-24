from dataclasses import dataclass, field

from src.domain.document import DocumentGraph


@dataclass(slots=True)
class ParsingWorkflowResult:
    document_id: str
    file_path: str
    page_count: int | None
    element_count: int
    section_count: int
    chunk_count: int
    table_count: int
    picture_count: int
    document_graph: DocumentGraph
    parse_confidence: float | None = None
    orphan_element_count: int = 0
    elements_without_page_count: int = 0
    parse_warnings: list[str] = field(default_factory=list)
