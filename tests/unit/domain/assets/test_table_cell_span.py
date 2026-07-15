from src.domain.assets.table_cell_span import TableCellSpan


def test_row_span_and_col_span_computed_from_start_end() -> None:
    span = TableCellSpan(row_start=1, row_end=2, col_start=0, col_end=3, text="Value")

    assert span.row_span == 2
    assert span.col_span == 4


def test_row_span_and_col_span_are_never_less_than_one() -> None:
    span = TableCellSpan(row_start=5, row_end=2, col_start=3, col_end=0, text="")

    assert span.row_span == 1
    assert span.col_span == 1


def test_to_dict_includes_derived_spans_and_all_fields() -> None:
    span = TableCellSpan(
        row_start=0,
        row_end=1,
        col_start=0,
        col_end=0,
        text="Parameter",
        normalized_text="parameter",
        raw_lines=["Param", "eter"],
    )

    data = span.to_dict()

    assert data == {
        "row_start": 0,
        "row_end": 1,
        "col_start": 0,
        "col_end": 0,
        "row_span": 2,
        "col_span": 1,
        "text": "Parameter",
        "normalized_text": "parameter",
        "raw_lines": ["Param", "eter"],
    }


def test_from_dict_defaults_row_end_and_col_end_to_start_when_missing() -> None:
    span = TableCellSpan.from_dict({"row_start": 2, "col_start": 3, "text": "X"})

    assert span.row_start == 2
    assert span.row_end == 2
    assert span.col_start == 3
    assert span.col_end == 3
    assert span.normalized_text is None
    assert span.raw_lines == []


def test_from_dict_filters_blank_raw_lines() -> None:
    span = TableCellSpan.from_dict(
        {
            "row_start": 0,
            "row_end": 0,
            "col_start": 0,
            "col_end": 0,
            "text": "A",
            "raw_lines": ["A", "  ", "", "B"],
        }
    )

    assert span.raw_lines == ["A", "B"]


def test_to_dict_from_dict_round_trips() -> None:
    original = TableCellSpan(
        row_start=1,
        row_end=1,
        col_start=2,
        col_end=4,
        text="900.123.456",
        normalized_text="900123456",
        raw_lines=["900.123.456"],
    )

    restored = TableCellSpan.from_dict(original.to_dict())

    assert restored == original


def test_list_from_data_returns_empty_list_for_non_list_input() -> None:
    assert TableCellSpan.list_from_data(None) == []
    assert TableCellSpan.list_from_data({"row_start": 0}) == []
    assert TableCellSpan.list_from_data("not a list") == []


def test_list_from_data_skips_non_dict_entries() -> None:
    spans = TableCellSpan.list_from_data(
        [
            {"row_start": 0, "row_end": 0, "col_start": 0, "col_end": 0, "text": "A"},
            "garbage",
            None,
            {"row_start": 1, "row_end": 1, "col_start": 0, "col_end": 0, "text": "B"},
        ]
    )

    assert [span.text for span in spans] == ["A", "B"]
