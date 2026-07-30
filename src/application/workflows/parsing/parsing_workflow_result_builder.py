from src.application.workflows.parsing.parsing_workflow_metrics import (
    collect_parse_warnings,
    compute_parse_confidence,
)
from src.application.workflows.parsing.parsing_workflow_result import (
    ParsingWorkflowResult,
)
from src.domain.document import DocumentGraph


def build_parsing_workflow_result(
    *,
    document_graph: DocumentGraph,
    file_path: str,
    page_count: int | None,
    ocr_trace=None,
    stage_durations: dict[str, float] | None = None,
    normalization_item_errors: list[str] | None = None,
) -> ParsingWorkflowResult:
    elements = list(document_graph.elements.values())
    orphan_count = sum(1 for e in elements if e.parent_section_id is None)
    no_page_count = sum(
        1 for e in elements if e.source.page_start is None
    )
    parse_confidence = compute_parse_confidence(
        element_count=len(elements),
        orphan_count=orphan_count,
        no_page_count=no_page_count,
    )
    warnings = collect_parse_warnings(
        element_count=len(elements),
        orphan_count=orphan_count,
        no_page_count=no_page_count,
        section_count=len(document_graph.sections),
        chunk_count=len(document_graph.chunks),
    )
    if ocr_trace is not None:
        warnings.extend(
            warning
            for warning in ocr_trace.warnings
            if warning not in warnings
        )
    if normalization_item_errors:
        warnings.append(
            f"{len(normalization_item_errors)} element(s) skipped during "
            "normalization due to per-item errors: "
            f"{'; '.join(normalization_item_errors[:5])}"
        )
    return ParsingWorkflowResult(
        document_id=document_graph.document.document_id,
        file_path=file_path,
        page_count=page_count,
        element_count=len(elements),
        section_count=len(document_graph.sections),
        chunk_count=len(document_graph.chunks),
        table_count=len(document_graph.tables),
        picture_count=len(document_graph.pictures),
        document_graph=document_graph,
        parse_confidence=parse_confidence,
        orphan_element_count=orphan_count,
        elements_without_page_count=no_page_count,
        parse_warnings=warnings,
        ocr_trace=ocr_trace,
        stage_durations=stage_durations or {},
    )
