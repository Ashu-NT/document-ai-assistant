from src.application.workflows.parsing.normalizers.table_layout.docling_parallel_table_reconstructor import (
    DoclingParallelTableReconstructor,
)
from src.domain.assets import TableCellSpan
from src.domain.common import BoundingBox


def _span(*, row, col, text, x1, x2, page=1) -> TableCellSpan:
    return TableCellSpan(
        row_start=row,
        row_end=row,
        col_start=col,
        col_end=col,
        text=text,
        page_number=page,
        bbox=BoundingBox(x1=x1, y1=100 + (row * 20), x2=x2, y2=118 + (row * 20)),
    )


def _two_lane_spans() -> list[TableCellSpan]:
    return [
        _span(row=0, col=0, text="Parameter", x1=40, x2=250),
        _span(row=0, col=1, text="Value", x1=260, x2=330),
        _span(row=1, col=0, text="Voltage", x1=40, x2=250),
        _span(row=1, col=1, text="400V", x1=260, x2=330),
        _span(row=0, col=2, text="Parameter", x1=620, x2=830),
        _span(row=0, col=3, text="Value", x1=840, x2=910),
        _span(row=1, col=2, text="Frequency", x1=620, x2=830),
        _span(row=1, col=3, text="50Hz", x1=840, x2=910),
    ]


def _vertically_misaligned_two_lane_spans() -> list[TableCellSpan]:
    return [
        _span(row=0, col=0, text="Task", x1=40, x2=250),
        _span(row=0, col=1, text="Daily", x1=260, x2=330),
        _span(row=1, col=0, text="Inspect pump", x1=40, x2=250),
        _span(row=1, col=1, text="x", x1=260, x2=330),
        _span(row=8, col=2, text="Task", x1=620, x2=830),
        _span(row=8, col=3, text="Weekly", x1=840, x2=910),
        _span(row=9, col=2, text="Replace seal", x1=620, x2=830),
        _span(row=9, col=3, text="x", x1=840, x2=910),
    ]


def test_reconstruct_returns_identical_result_regardless_of_page_lane_count() -> None:
    reconstructor = DoclingParallelTableReconstructor()
    spans = _two_lane_spans()

    without_hint = reconstructor.reconstruct(spans)
    with_matching_hint = reconstructor.reconstruct(spans, page_lane_count=2)
    with_mismatched_hint = reconstructor.reconstruct(spans, page_lane_count=1)

    assert without_hint.parallel_stream_rows == with_matching_hint.parallel_stream_rows
    assert without_hint.parallel_stream_rows == with_mismatched_hint.parallel_stream_rows
    assert without_hint.rows == with_matching_hint.rows == with_mismatched_hint.rows
    assert without_hint.parallel_stream_rows == [
        [["Parameter", "Value"], ["Voltage", "400V"]],
        [["Parameter", "Value"], ["Frequency", "50Hz"]],
    ]
    assert [item.stream_index for item in without_hint.parallel_stream_descriptors] == [1, 2]
    assert [item.page_number for item in without_hint.parallel_stream_descriptors] == [1, 1]
    assert [item.column_count for item in without_hint.parallel_stream_descriptors] == [2, 2]


def test_reconstruct_logs_disagreement_when_page_lane_count_mismatches(caplog) -> None:
    reconstructor = DoclingParallelTableReconstructor()
    spans = _two_lane_spans()

    with caplog.at_level("INFO"):
        reconstructor.reconstruct(spans, page_lane_count=1)

    assert "parallel_table_stream_lane_count_disagreement" in caplog.text


def test_reconstruct_does_not_log_when_page_lane_count_matches(caplog) -> None:
    reconstructor = DoclingParallelTableReconstructor()
    spans = _two_lane_spans()

    with caplog.at_level("INFO"):
        reconstructor.reconstruct(spans, page_lane_count=2)

    assert "parallel_table_stream_lane_count_disagreement" not in caplog.text


def test_reconstruct_rejects_x_parallel_clusters_when_vertical_bands_do_not_align() -> None:
    reconstructor = DoclingParallelTableReconstructor()

    reconstructed = reconstructor.reconstruct(_vertically_misaligned_two_lane_spans())

    assert reconstructed is None
