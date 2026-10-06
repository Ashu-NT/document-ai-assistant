from src.application.workflows.extraction.table_windowing.table_evidence_window_builder import (
    TableEvidenceWindowBuilder,
)
from src.domain.assets import TableAsset

# Generic-mechanism tests: deliberately use a SYNTHETIC table, not anything
# MaintenanceTask-specific, per the architecture clarification ("Generic
# mechanism tests should NOT depend on MaintenanceTask").

_HEADER = ["Row ID", "Component", "Description"]


def _make_table(row_count: int, *, table_id: str = "table_001") -> TableAsset:
    data_rows = [
        [f"ID{n:03d}", f"Component {n}", f"Description of task {n}"]
        for n in range(1, row_count + 1)
    ]
    return TableAsset(
        table_id=table_id,
        document_id="doc_001",
        markdown="irrelevant markdown - the builder must not use this",
        rows=[_HEADER, *data_rows],
    )


def test_39_row_table_splits_into_four_windows_of_10_10_10_9() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    assert len(windows) == 4
    assert [(w.row_start, w.row_end) for w in windows] == [
        (1, 10),
        (11, 20),
        (21, 30),
        (31, 39),
    ]
    assert all(w.window_count == 4 for w in windows)
    assert [w.window_index for w in windows] == [1, 2, 3, 4]
    assert all(w.total_row_count == 39 for w in windows)


def test_header_appears_in_every_window() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    for window in windows:
        assert "Row ID" in window.rendered_text
        assert "Component" in window.rendered_text
        assert "Description" in window.rendered_text


def test_rows_appear_exactly_once_across_non_overlapping_windows() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    for row_number in range(1, 40):
        marker = f"ID{row_number:03d}"
        occurrences = sum(window.rendered_text.count(marker) for window in windows)
        assert occurrences == 1, f"row {row_number} appeared {occurrences} times"


def test_row_order_is_preserved_within_each_window() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    first_window_text = windows[0].rendered_text
    positions = [first_window_text.find(f"ID{n:03d}") for n in range(1, 11)]
    assert positions == sorted(positions)
    assert all(p != -1 for p in positions)


def test_no_row_is_lost() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    combined = "\n".join(w.rendered_text for w in windows)
    for row_number in range(1, 40):
        assert f"ID{row_number:03d}" in combined


def test_no_row_is_duplicated_within_a_single_window() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    for window in windows:
        row_count_in_window = window.row_end - window.row_start + 1
        for offset in range(row_count_in_window):
            marker = f"ID{window.row_start + offset:03d}"
            assert window.rendered_text.count(marker) == 1


def test_window_rendering_does_not_duplicate_the_tables_raw_markdown() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    for window in windows:
        assert table.markdown not in window.rendered_text


def test_table_at_or_under_the_row_threshold_produces_a_single_window() -> None:
    table = _make_table(10)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_001")

    assert len(windows) == 1
    assert (windows[0].row_start, windows[0].row_end) == (1, 10)


def test_should_window_is_false_at_or_under_threshold_and_true_above_it() -> None:
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    assert builder.should_window(_make_table(10)) is False
    assert builder.should_window(_make_table(11)) is True
    assert builder.should_window(_make_table(39)) is True


def test_source_chunk_id_is_preserved_verbatim_never_a_synthetic_value() -> None:
    table = _make_table(39)
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    windows = builder.build_windows(table, source_chunk_id="chunk_canonical_xyz")

    assert all(w.source_chunk_id == "chunk_canonical_xyz" for w in windows)
    # execution_window_id is a distinct, internal-only identity - never
    # equal to the canonical source_chunk_id.
    assert all(w.execution_window_id != w.source_chunk_id for w in windows)
    assert all(w.execution_window_id.startswith("chunk_canonical_xyz::") for w in windows)
