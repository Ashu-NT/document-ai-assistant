from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.builders.maintenance_task_builder import (
    MaintenanceTaskBuilder,
)
from src.application.workflows.extraction.context import SemanticExtractionContextBuilder
from src.domain.assets import TableAsset
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.shared.ids import IdGenerator

_HEADER = ["Parameter", "Item", "Maintenance tasks", "Option"]
_ROWS = [
    _HEADER,
    [
        "WM00063", "LUBE OIL SYSTEM",
        "Check layer thickness of oil residue on automatic centrifugal oil "
        "filter, clean, and replace paper element at every engine oil "
        "change at the latest",
        "",
    ],
    ["WM00084", "FUEL SYSTEM (LOW PRESSURE)", "Fuel prefilter, replace filter", "X"],
    [
        "WM00085", "FUEL SYSTEM (LOW PRESSURE)",
        "Additional fuel filter: Replace easy-change fuel filter", "X",
    ],
    ["WM00086", "FUEL SYSTEM (LOW PRESSURE)", "Replace easy-change fuel filter", ""],
]


def _make_table(rows: list[list[str]] | None = None) -> TableAsset:
    return TableAsset(
        table_id="table_001", document_id="doc_001",
        markdown="irrelevant canonical markdown", rows=rows or _ROWS,
    )


def _make_chunk(chunk_id: str = "chunk_window2") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content="irrelevant window rendering",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        table_ids=["table_001"],
        source=SourceLocation(page_start=67, page_end=68),
        table_row_start=1,
        table_row_end=4,
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
        tables={"table_001": _make_table()},
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
        tables={"table_001": _make_table()},
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
        tables={"table_001": _make_table()},
    )

    assert task.task_code is None
    assert task.requires_human_review is False


def test_duplicate_code_in_canonical_table_is_ambiguous_and_rejected() -> None:
    duplicated_rows = [
        _HEADER,
        ["WM00085", "FUEL SYSTEM (LOW PRESSURE)", "Additional fuel filter: Replace easy-change fuel filter", "X"],
        ["WM00085", "FUEL SYSTEM (HIGH PRESSURE)", "A different row that accidentally repeats the same code", ""],
    ]
    builder = _make_builder()
    chunk = _make_chunk()

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
        tables={"table_001": _make_table(duplicated_rows)},
    )

    assert task.task_code is None
    assert task.requires_human_review is True


def test_row_span_inherited_item_label_does_not_confuse_code_verification() -> None:
    """WM00084/85/86 all share the inherited 'Item' label FUEL SYSTEM (LOW
    PRESSURE) - verification must still distinguish each row by its own
    code+title, never by the shared component label."""
    builder = _make_builder()
    chunk = _make_chunk()
    tables = {"table_001": _make_table()}

    task_a = builder.build(
        {"title": "Fuel prefilter, replace filter", "task_code": "WM00084",
         "source_chunk_id": "chunk_window2"},
        document_id="doc_001", chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2", default_confidence=0.9, tables=tables,
    )
    task_b = builder.build(
        {"title": "Replace easy-change fuel filter", "task_code": "WM00086",
         "source_chunk_id": "chunk_window2"},
        document_id="doc_001", chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2", default_confidence=0.9, tables=tables,
    )

    assert task_a.task_code == "WM00084"
    assert task_b.task_code == "WM00086"


def test_swapped_code_with_mismatched_title_is_rejected() -> None:
    """The adversarial case this task targets: a VALID code (WM00086,
    really present in the table) paired with a DIFFERENT row's title
    (WM00085's). WM00086's own row text never mentions "additional fuel
    filter", so this must be rejected, not silently accepted."""
    builder = _make_builder()
    chunk = _make_chunk()

    task = builder.build(
        {
            "title": "Additional fuel filter: Replace easy-change fuel filter",
            "task_code": "WM00086",
            "source_chunk_id": "chunk_window2",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_window2": chunk},
        default_source_chunk_id="chunk_window2",
        default_confidence=0.9,
        tables={"table_001": _make_table()},
    )

    assert task.task_code is None
    assert task.requires_human_review is True


def test_no_canonical_table_available_falls_back_to_unverified() -> None:
    """Without a resolvable canonical table, a claimed code can never be
    trusted - this is the safe default, not a chunk-wide text fallback."""
    builder = _make_builder()
    chunk = _make_chunk()

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
        tables=None,
    )

    assert task.task_code is None
    assert task.requires_human_review is True
