from src.application.workflows.parsing.normalizers.table_layout.parallel_streams.parallel_table_stream_clusterer import (
    ParallelTableStreamClusterer,
)
from src.domain.assets import TableCellSpan
from src.domain.common import BoundingBox


def _make_span(*, row: int, col: int, x1: float, x2: float, page: int = 1) -> TableCellSpan:
    return TableCellSpan(
        row_start=row,
        row_end=row,
        col_start=col,
        col_end=col,
        text=f"cell_{row}_{col}",
        bbox=BoundingBox(x1=x1, y1=100 + row * 20, x2=x2, y2=118 + row * 20),
        page_number=page,
    )


def _two_lane_spans() -> list[TableCellSpan]:
    spans = []
    for row in range(3):
        spans.append(_make_span(row=row, col=0, x1=40, x2=250))
        spans.append(_make_span(row=row, col=1, x1=620, x2=830))
    return spans


def test_cluster_returns_same_groups_regardless_of_page_lane_count() -> None:
    clusterer = ParallelTableStreamClusterer()
    spans = _two_lane_spans()

    without_hint = clusterer.cluster(spans)
    with_matching_hint = clusterer.cluster(spans, page_lane_count=2)
    with_mismatched_hint = clusterer.cluster(spans, page_lane_count=1)

    assert without_hint == with_matching_hint == with_mismatched_hint
    assert len(without_hint) == 2


def test_cluster_logs_disagreement_when_page_lane_count_mismatches(caplog) -> None:
    clusterer = ParallelTableStreamClusterer()
    spans = _two_lane_spans()

    with caplog.at_level("INFO"):
        clusterer.cluster(spans, page_lane_count=1)

    assert "parallel_table_stream_lane_count_disagreement" in caplog.text
    assert "cell_cluster_count=2" in caplog.text
    assert "page_lane_count=1" in caplog.text


def test_cluster_does_not_log_when_page_lane_count_matches(caplog) -> None:
    clusterer = ParallelTableStreamClusterer()
    spans = _two_lane_spans()

    with caplog.at_level("INFO"):
        clusterer.cluster(spans, page_lane_count=2)

    assert "parallel_table_stream_lane_count_disagreement" not in caplog.text


def test_cluster_does_not_log_when_page_lane_count_is_absent(caplog) -> None:
    clusterer = ParallelTableStreamClusterer()
    spans = _two_lane_spans()

    with caplog.at_level("INFO"):
        clusterer.cluster(spans)

    assert "parallel_table_stream_lane_count_disagreement" not in caplog.text


def test_cluster_below_span_threshold_still_honors_page_lane_count_logging(caplog) -> None:
    clusterer = ParallelTableStreamClusterer()
    spans = [_make_span(row=0, col=0, x1=40, x2=250)]

    with caplog.at_level("INFO"):
        result = clusterer.cluster(spans, page_lane_count=2)

    assert result == []
    assert "parallel_table_stream_lane_count_disagreement" in caplog.text
    assert "cell_cluster_count=0" in caplog.text
