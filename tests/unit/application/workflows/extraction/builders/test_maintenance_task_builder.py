from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.builders.maintenance_task_builder import (
    MaintenanceTaskBuilder,
)
from src.application.workflows.extraction.context import SemanticExtractionContextBuilder
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.shared.ids import IdGenerator

_WINDOW_CONTENT = (
    "Table header: Task | Item | Maintenance tasks | Option\n"
    "This is window 2/4 of a larger table: rows 11-20 of 39 total rows.\n"
    "Row 11: Task=WM00063 | Item=LUBE OIL SYSTEM | Maintenance tasks=Check layer thickness\n"
    "Row 13: Task=WM00084 | Item=FUEL SYSTEM (LOW PRESSURE) | Maintenance tasks=Fuel prefilter, replace filter\n"
    "Row 14: Task=WM00085 | Item=FUEL SYSTEM (LOW PRESSURE) | Maintenance tasks=Additional fuel filter: Replace easy-change fuel filter\n"
    "Row 15: Task=WM00086 | Item=FUEL SYSTEM (LOW PRESSURE) | Maintenance tasks=Replace easy-change fuel filter\n"
)


def _make_chunk(chunk_id: str = "chunk_window2", content: str = _WINDOW_CONTENT) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        source=SourceLocation(page_start=67, page_end=68),
        table_row_start=11,
        table_row_end=20,
    )


def _make_builder(chunks: list[DocumentChunk] | None = None) -> MaintenanceTaskBuilder:
    support = ExtractionBuilderSupport(confidence_threshold=0.5, require_human_review_default=False)
    if chunks:
        support.set_semantic_contexts(
            SemanticExtractionContextBuilder().build_all(document_id="doc_001", chunks=chunks)
        )
    return MaintenanceTaskBuilder(IdGenerator(), support)


def test_verified_task_code_is_preserved_and_grounds_table_row_id() -> None:
    chunk = _make_chunk()
    builder = _make_builder([chunk])

    task = builder.build(
        {
            "title": "Additional fuel filter: Replace easy-change fuel filter",
            "component_name": "FUEL SYSTEM (LOW PRESSURE)",
            "task_code": "WM00085",
            "source_chunk_id": "chunk_window2",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2",
        default_confidence=0.9,
    )

    assert task.task_code == "WM00085"
    assert task.requires_human_review is False
    assert task.source_metadata is not None
    assert task.source_metadata.table_row_id == "WM00085"


def test_invalid_hallucinated_task_code_is_discarded_and_flagged() -> None:
    builder = _make_builder()
    chunk = _make_chunk()
    support = builder._support

    task = builder.build(
        {
            "title": "Replace easy-change fuel filter",
            "component_name": "FUEL SYSTEM (LOW PRESSURE)",
            "task_code": "WM99999",
            "source_chunk_id": "chunk_window2",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2",
        default_confidence=0.9,
    )

    assert task.task_code is None
    assert task.requires_human_review is True
    assert support.maintenance_task_unverified_code_events == [
        {"source_chunk_id": "chunk_window2", "claimed_task_code": "WM99999"}
    ]


def test_missing_task_code_falls_back_without_flagging() -> None:
    builder = _make_builder()
    chunk = _make_chunk()

    task = builder.build(
        {
            "title": "Replace easy-change fuel filter",
            "component_name": "FUEL SYSTEM (LOW PRESSURE)",
            "source_chunk_id": "chunk_window2",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2",
        default_confidence=0.9,
    )

    assert task.task_code is None
    assert task.requires_human_review is False


def test_ambiguous_repeated_code_in_content_is_still_accepted_as_grounded() -> None:
    builder = _make_builder()
    chunk = _make_chunk(
        content=_WINDOW_CONTENT + "Row 14 (continued): Task=WM00085 appears again in a footnote.\n"
    )

    task = builder.build(
        {
            "title": "Additional fuel filter: Replace easy-change fuel filter",
            "task_code": "WM00085",
            "source_chunk_id": "chunk_window2",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2",
        default_confidence=0.9,
    )

    assert task.task_code == "WM00085"
    assert task.requires_human_review is False


def test_row_span_inherited_item_label_does_not_confuse_code_verification() -> None:
    """Multiple rows sharing the same inherited 'Item' label (a common
    row-span pattern) must not interfere with per-row task_code grounding."""
    builder = _make_builder()
    chunk = _make_chunk()

    task_a = builder.build(
        {"title": "Fuel prefilter, replace filter", "task_code": "WM00084",
         "source_chunk_id": "chunk_window2"},
        document_id="doc_001", chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2", default_confidence=0.9,
    )
    task_b = builder.build(
        {"title": "Replace easy-change fuel filter", "task_code": "WM00086",
         "source_chunk_id": "chunk_window2"},
        document_id="doc_001", chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2", default_confidence=0.9,
    )

    assert task_a.task_code == "WM00084"
    assert task_b.task_code == "WM00086"
