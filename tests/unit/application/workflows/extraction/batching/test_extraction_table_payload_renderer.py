from src.application.workflows.extraction.batching.table_payload import (
    ExtractionTablePayloadRenderer,
)
from src.domain.assets import TableAsset, TableParallelStream


def test_renderer_builds_structured_specification_payload() -> None:
    renderer = ExtractionTablePayloadRenderer()
    table = TableAsset(
        table_id="table_spec",
        document_id="doc_001",
        markdown=(
            "| Parameter | Compact version | Remote version |\n"
            "|---|---|---|\n"
            "| Pressure range | 0...10 | 0...16 |"
        ),
        rows=[
            ["Parameter", "Compact version", "Remote version"],
            ["Pressure range", "0...10", "0...16"],
        ],
        table_shape="specification_matrix",
        header_paths=[
            ["Parameter"],
            ["Field", "Compact version"],
            ["Field", "Remote version"],
        ],
    )

    rendered = renderer.render(table)

    assert rendered is not None
    assert "Structured specification records:" in rendered
    assert "Row 1: Parameter=Pressure range" in rendered
    assert "Compact version=0...10" in rendered
    assert "Remote version=0...16" in rendered


def test_renderer_builds_structured_maintenance_schedule_payload() -> None:
    renderer = ExtractionTablePayloadRenderer()
    table = TableAsset(
        table_id="table_schedule",
        document_id="doc_001",
        markdown=(
            "| Task | D | W | Notes |\n"
            "|---|---|---|---|\n"
            "| Inspect filter | x |  | Before startup |\n"
            "| Clean housing |  | x | Use fresh water |"
        ),
        rows=[
            ["Task", "D", "W", "Notes"],
            ["Inspect filter", "x", "", "Before startup"],
            ["Clean housing", "", "x", "Use fresh water"],
        ],
        table_shape="maintenance_schedule_matrix",
        header_paths=[["Task"], ["Interval", "Daily"], ["Interval", "Weekly"], ["Notes"]],
    )

    rendered = renderer.render(table)

    assert rendered is not None
    assert "Structured maintenance schedule:" in rendered
    assert "Intervals=Daily" in rendered
    assert "Intervals=Weekly" in rendered
    assert "Notes=Before startup" in rendered


def test_renderer_builds_structured_performance_curve_payload() -> None:
    renderer = ExtractionTablePayloadRenderer()
    table = TableAsset(
        table_id="table_curve",
        document_id="doc_001",
        markdown="curve",
        rows=[
            ["Pump type", "Motor power", "Motor power", "Q m3/h", "0", "1", "1.5"],
            ["Pump type", "kW", "HP", "Q l/min", "0", "16.6", "25"],
            ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
        ],
        table_shape="performance_curve_matrix",
    )

    rendered = renderer.render(table)

    assert rendered is not None
    assert "Structured performance data:" in rendered
    assert "Pump type=MXV 25-220C" in rendered
    assert "Curve metric=H m" in rendered
    assert "Curve points=" in rendered


def test_renderer_builds_structured_spare_parts_payload() -> None:
    renderer = ExtractionTablePayloadRenderer()
    table = TableAsset(
        table_id="table_spare",
        document_id="doc_001",
        markdown="spares",
        rows=[
            [
                "Part Pos. Qty Unit",
                "Designation Size / Dimension, Material / Surface",
                "Part No",
            ],
            ["0010 1 Pce", "housing", ""],
            ["P31 1", "Disassembly screw for carrier", "-18/02 2"],
        ],
        table_category="spare_parts_table",
    )

    rendered = renderer.render(table)

    assert rendered is not None
    assert "Structured spare-parts records:" in rendered
    assert "Position=0010" in rendered
    assert "Part No.=-18/02" in rendered


def test_renderer_builds_structured_troubleshooting_payload() -> None:
    renderer = ExtractionTablePayloadRenderer()
    table = TableAsset(
        table_id="table_troubleshooting",
        document_id="doc_001",
        markdown="troubleshooting",
        rows=[
            ["Symptom", "Probable cause", "Remedy"],
            ["Pump does not start", "No power supply", "Check fuse"],
        ],
        table_category="troubleshooting_table",
    )

    rendered = renderer.render(table)

    assert rendered is not None
    assert "Structured troubleshooting records:" in rendered
    assert "Symptom=Pump does not start" in rendered
    assert "Cause=No power supply" in rendered
    assert "Remedy=Check fuse" in rendered


def test_renderer_renders_parallel_stream_payloads_separately() -> None:
    renderer = ExtractionTablePayloadRenderer()
    table = TableAsset(
        table_id="table_parallel",
        document_id="doc_001",
        markdown="parallel",
        rows=[["Unused", "Unused"], ["x", "y"]],
        parallel_stream_rows=[
            [["Parameter", "Value"], ["Voltage", "400V"]],
            [["Parameter", "Value"], ["Frequency", "50Hz"]],
        ],
        parallel_stream_descriptors=[
            TableParallelStream(
                stream_index=1,
                source_row_start=0,
                source_row_end=1,
                source_col_start=0,
                source_col_end=1,
                row_count=2,
                column_count=2,
                page_number=3,
            ),
            TableParallelStream(
                stream_index=2,
                source_row_start=0,
                source_row_end=1,
                source_col_start=2,
                source_col_end=3,
                row_count=2,
                column_count=2,
                page_number=3,
            ),
        ],
        table_shape="specification_matrix",
        header_paths=[["Parameter"], ["Value"]],
    )

    rendered = renderer.render(table)

    assert rendered is not None
    assert "Parallel Table Stream 1 (Left):" in rendered
    assert "Parallel Table Stream 2 (Right):" in rendered
    assert "Parameter=Voltage | Value=400V" in rendered
    assert "Parameter=Frequency | Value=50Hz" in rendered
