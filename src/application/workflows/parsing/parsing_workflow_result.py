from dataclasses import dataclass, field

from src.application.contracts.pdf_links import PdfLinkExtractionResult
from src.application.workflows.parsing.builders.document_graph.cross_references import (
    CrossReferenceLinkingOutcome,
)
from src.domain.document import DocumentGraph
from src.application.workflows.parsing.ocr import OCRTrace


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
    ocr_trace: OCRTrace | None = None
    stage_durations: dict[str, float] = field(default_factory=dict)
    # Explicit return-value replacements for what used to be read back from
    # ParsingWorkflow.last_pdf_link_extraction_result / DocumentGraphBuilder.
    # last_cross_reference_linking_outcome after the call returned - both
    # were unsafe under concurrent reuse of a shared workflow/builder
    # instance (see the concurrent-parsing investigation).
    pdf_link_extraction_result: PdfLinkExtractionResult | None = None
    cross_reference_linking_outcome: CrossReferenceLinkingOutcome | None = None
