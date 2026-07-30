from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.application.workflows.parsing.normalizers.table_layout.text_grid.text_grid_table_fallback_applier import (
    TextGridTableFallbackApplier,
)
from src.domain.common import BoundingBox, ElementType


def _text_element(
    element_id: str,
    text: str,
    *,
    page: int,
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    order_index: int,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_1",
        element_type=ElementType.TEXT,
        text=text,
        page_start=page,
        page_end=page,
        bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
        order_index=order_index,
        section_path=["Information"],
        section_title="Information",
    )


def _grid_row_elements(
    *,
    start_index: int,
    start_order: int,
    page: int,
    label: str,
    value: str,
    y1: float,
    y2: float,
) -> list[ParsedCanonicalElement]:
    return [
        _text_element(
            f"el_{start_index}",
            label,
            page=page,
            x1=50.0,
            x2=60.0,
            y1=y1,
            y2=y2,
            order_index=start_order,
        ),
        _text_element(
            f"el_{start_index + 1}",
            value,
            page=page,
            x1=200.0,
            x2=260.0,
            y1=y1,
            y2=y2,
            order_index=start_order + 1,
        ),
    ]


def _loose_grid_elements(page: int = 1) -> list[ParsedCanonicalElement]:
    elements: list[ParsedCanonicalElement] = []
    for row_index in range(4):
        elements.extend(
            _grid_row_elements(
                start_index=row_index * 2,
                start_order=row_index * 2 + 1,
                page=page,
                label=str(row_index + 1),
                value=f"1615.{row_index}",
                y1=400.0 - row_index * 20,
                y2=392.0 - row_index * 20,
            )
        )
    return elements


def test_apply_replaces_a_detected_grid_with_one_synthetic_table_element() -> None:
    applier = TextGridTableFallbackApplier()
    elements = _loose_grid_elements()

    result = applier.apply(elements)

    tables = [element for element in result if element.element_type == ElementType.TABLE]
    assert len(tables) == 1
    table = tables[0]
    assert table.metadata["table_structure_tier"] == "text_grid_fallback"
    assert table.metadata["table_rows"] == [
        ["", ""],
        ["1", "1615.0"],
        ["2", "1615.1"],
        ["3", "1615.2"],
        ["4", "1615.3"],
    ]
    # All 8 original loose text elements are gone, replaced by exactly the
    # one synthetic table.
    assert len(result) == 1


def test_apply_renumbers_order_index_sequentially_after_synthesis() -> None:
    applier = TextGridTableFallbackApplier()
    elements = [
        _text_element(
            "el_before", "Section overview", page=1, x1=50, x2=300, y1=500, y2=480, order_index=1
        ),
        *_loose_grid_elements(),
        _text_element(
            "el_after", "Next section", page=1, x1=50, x2=300, y1=200, y2=180, order_index=99
        ),
    ]

    result = applier.apply(elements)

    assert [element.order_index for element in result] == list(range(1, len(result) + 1))
    assert [element.element_id for element in result] == [
        "el_before",
        "el_0_text_grid_table",
        "el_after",
    ]


def test_apply_does_not_touch_text_elements_already_covered_by_an_existing_table() -> None:
    applier = TextGridTableFallbackApplier()
    grid_elements = _loose_grid_elements()
    existing_table = ParsedCanonicalElement(
        element_id="el_real_table",
        document_id="doc_1",
        element_type=ElementType.TABLE,
        text="| a | b |",
        page_start=1,
        page_end=1,
        bbox=BoundingBox(x1=0.0, y1=410.0, x2=280.0, y2=300.0),
        order_index=0,
        metadata={"table_rows": [["a", "b"]]},
    )

    result = applier.apply([existing_table, *grid_elements])

    # Every loose element overlaps the existing table's bbox, so none of
    # them are eligible candidates -- nothing should be synthesized, and
    # the existing table must survive untouched.
    assert result == [existing_table, *grid_elements]


def test_apply_returns_input_unchanged_when_no_page_has_a_detectable_grid() -> None:
    applier = TextGridTableFallbackApplier()
    elements = [
        _text_element(
            "el_1", "Just an ordinary paragraph of text.", page=1, x1=50, x2=400, y1=500, y2=480, order_index=1
        ),
        _text_element(
            "el_2", "Another ordinary paragraph.", page=1, x1=50, x2=400, y1=470, y2=450, order_index=2
        ),
    ]

    result = applier.apply(elements)

    assert result == elements


def _toc_row_elements(
    *,
    start_index: int,
    page: int,
    title: str,
    page_number: str,
    y1: float,
    y2: float,
) -> list[ParsedCanonicalElement]:
    return [
        _text_element(
            f"el_{start_index}", title, page=page, x1=50.0, x2=250.0, y1=y1, y2=y2,
            order_index=start_index,
        ),
        _text_element(
            f"el_{start_index + 1}", "................................", page=page,
            x1=260.0, x2=340.0, y1=y1, y2=y2, order_index=start_index + 1,
        ),
        _text_element(
            f"el_{start_index + 2}", page_number, page=page, x1=350.0, x2=360.0,
            y1=y1, y2=y2, order_index=start_index + 2,
        ),
    ]


def _orphaned_toc_elements(page: int = 1) -> list[ParsedCanonicalElement]:
    rows = [
        ("1.1 First topic", "1"),
        ("1.2 Second topic", "2"),
        ("1.3 Third topic", "3"),
        ("1.4 Fourth topic", "4"),
    ]
    elements: list[ParsedCanonicalElement] = []
    for row_index, (title, page_number) in enumerate(rows):
        elements.extend(
            _toc_row_elements(
                start_index=row_index * 3,
                page=page,
                title=title,
                page_number=page_number,
                y1=400.0 - row_index * 20,
                y2=392.0 - row_index * 20,
            )
        )
    return elements


def test_apply_falls_back_to_orphaned_toc_reconstruction_when_grid_detection_fails() -> None:
    # A dot-leader TOC list is NOT a regular record grid (TextGridTableDetector
    # correctly finds nothing here), so the applier must fall through to the
    # second strategy rather than giving up on the page.
    applier = TextGridTableFallbackApplier()

    result = applier.apply(_orphaned_toc_elements())

    tables = [element for element in result if element.element_type == ElementType.TABLE]
    assert len(tables) == 1
    table = tables[0]
    assert table.metadata["table_structure_tier"] == "orphaned_toc_reconstruction"
    assert table.metadata["table_rows"] == [
        ["Number", "Title", "Page"],
        ["1.1", "First topic", "1"],
        ["1.2", "Second topic", "2"],
        ["1.3", "Third topic", "3"],
        ["1.4", "Fourth topic", "4"],
    ]
