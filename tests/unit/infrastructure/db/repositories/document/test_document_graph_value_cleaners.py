from src.infrastructure.db.repositories.document.document_graph_value_cleaners import (
    clean_axis_summary,
    clean_header_paths,
    clean_multiline_text,
    clean_parallel_stream_rows,
    clean_rows,
    clean_text,
    coerce_float,
    coerce_int,
)


def test_clean_text_returns_none_for_blank_input() -> None:
    assert clean_text(None) is None
    assert clean_text("   ") is None


def test_clean_text_strips_and_repairs_mojibake() -> None:
    mojibake = b"Don\xe2\x80\x99t".decode("cp1252")
    assert clean_text(f"  {mojibake}  ") == "Don’t"


def test_clean_multiline_text_returns_none_for_none_input() -> None:
    assert clean_multiline_text(None) is None


def test_clean_multiline_text_joins_stripped_lines() -> None:
    assert clean_multiline_text("  line one  \n  line two  ") == "line one\nline two"


def test_clean_rows_returns_empty_list_for_non_list_input() -> None:
    assert clean_rows(None) == []
    assert clean_rows("not a list") == []


def test_clean_rows_skips_non_list_rows_and_cleans_cells() -> None:
    assert clean_rows([["  A  ", "B"], "not a row", [None]]) == [["A", "B"], [""]]


def test_clean_parallel_stream_rows_returns_empty_list_for_non_list_input() -> None:
    assert clean_parallel_stream_rows(None) == []


def test_clean_parallel_stream_rows_drops_streams_with_no_real_rows() -> None:
    assert clean_parallel_stream_rows([[["A"]], [], "not a stream"]) == [[["A"]]]


def test_coerce_float_returns_none_for_none_and_invalid_input() -> None:
    assert coerce_float(None) is None
    assert coerce_float("not a number") is None


def test_coerce_float_converts_numeric_input() -> None:
    assert coerce_float("0.75") == 0.75
    assert coerce_float(1) == 1.0


def test_coerce_int_returns_none_for_none_and_invalid_input() -> None:
    assert coerce_int(None) is None
    assert coerce_int("not a number") is None


def test_coerce_int_converts_numeric_input() -> None:
    assert coerce_int("2") == 2
    assert coerce_int(3.0) == 3


def test_clean_header_paths_returns_empty_list_for_non_list_input() -> None:
    assert clean_header_paths(None) == []


def test_clean_header_paths_drops_blank_parts_and_non_list_paths() -> None:
    assert clean_header_paths([["Task", "  "], "not a path", [None, "Interval"]]) == [
        ["Task"],
        ["Interval"],
    ]


def test_clean_axis_summary_returns_empty_dict_for_non_dict_input() -> None:
    assert clean_axis_summary(None) == {}


def test_clean_axis_summary_drops_entries_with_blank_key_or_value() -> None:
    assert clean_axis_summary({"row_axis": "task", "  ": "ignored", "col_axis": ""}) == {
        "row_axis": "task",
    }
