from dataclasses import dataclass

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
