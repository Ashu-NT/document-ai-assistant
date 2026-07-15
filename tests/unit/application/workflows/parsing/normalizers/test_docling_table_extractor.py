from src.application.workflows.parsing.normalizers.docling_table_extractor import (
    DoclingTableExtractor,
)


class _FakeCell:
    def __init__(
        self,
        *,
        start_row_offset_idx=None,
        end_row_offset_idx=None,
        start_col_offset_idx=None,
        end_col_offset_idx=None,
        text=None,
        prov=None,
    ) -> None:
        self.start_row_offset_idx = start_row_offset_idx
        self.end_row_offset_idx = end_row_offset_idx
        self.start_col_offset_idx = start_col_offset_idx
        self.end_col_offset_idx = end_col_offset_idx
        self.text = text
        self.prov = prov or []


class _FakeData:
    def __init__(self, table_cells: list[_FakeCell]) -> None:
        self.table_cells = table_cells


class _FakeTableItem:
    def __init__(self, table_cells: list[_FakeCell]) -> None:
        self.data = _FakeData(table_cells)


class _FakeBBox:
    def __init__(self, x1, y1, x2, y2) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class _FakeProvenance:
    def __init__(self, page_no, bbox=None) -> None:
        self.page_no = page_no
        self.bbox = bbox


def test_extract_dimensions_returns_none_for_no_table_cells() -> None:
    extractor = DoclingTableExtractor()

    assert extractor.extract_dimensions(_FakeTableItem([])) == (None, None)


def test_extract_dimensions_uses_the_maximum_end_offset_across_cells() -> None:
    extractor = DoclingTableExtractor()
    item = _FakeTableItem(
        [
            _FakeCell(
                start_row_offset_idx=0,
                end_row_offset_idx=1,
                start_col_offset_idx=0,
                end_col_offset_idx=1,
            ),
            _FakeCell(
                start_row_offset_idx=2,
                end_row_offset_idx=3,
                start_col_offset_idx=0,
                end_col_offset_idx=2,
            ),
        ]
    )

    assert extractor.extract_dimensions(item) == (3, 2)


def test_resolve_offset_end_does_not_treat_a_real_zero_as_missing() -> None:
    """Regression test: an end offset of exactly 0 is a real value, not
    a missing one - a plain `or` fallback would treat it as falsy and
    silently substitute `start_offset + 1` instead.
    """
    extractor = DoclingTableExtractor()
    cell = _FakeCell(start_row_offset_idx=0, end_row_offset_idx=0)

    resolved = extractor._resolve_offset_end(
        cell, "end_row_offset_idx", "start_row_offset_idx"
    )

    assert resolved == 0


def test_extract_cell_spans_preserves_optional_page_and_bbox_metadata() -> None:
    extractor = DoclingTableExtractor()
    item = _FakeTableItem(
        [
            _FakeCell(
                start_row_offset_idx=0,
                end_row_offset_idx=1,
                start_col_offset_idx=0,
                end_col_offset_idx=1,
                text="Title",
                prov=[_FakeProvenance(3, _FakeBBox(10, 20, 110, 40))],
            )
        ]
    )

    spans = extractor.extract_cell_spans(item)

    assert spans == [
        {
            "row_start": 0,
            "row_end": 0,
            "col_start": 0,
            "col_end": 0,
            "row_span": 1,
            "col_span": 1,
            "text": "Title",
            "normalized_text": "Title",
            "raw_lines": ["Title"],
            "page_number": 3,
            "bbox": {"x1": 10.0, "y1": 20.0, "x2": 110.0, "y2": 40.0},
        }
    ]
