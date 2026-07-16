from src.application.workflows.parsing.tables import TableSemanticResolver
from src.domain.assets import TableAsset
from src.domain.common import ElementType, ParserMetadata, SourceLocation
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.domain.elements import CanonicalElement


def _make_document() -> Document:
    return Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
    )


def test_table_semantic_resolver_persists_maintenance_structure_metadata() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| Task | D | W | M |",
        rows=[
            ["Task", "D", "W", "M"],
            ["Inspect basket", "x", "", "x"],
        ],
        row_count=2,
        column_count=4,
    )
    graph.add_element(
        CanonicalElement(
            element_id="el_table_1",
            document_id="doc_001",
            element_type=ElementType.TABLE,
            text="| Task | D | W | M |",
            table_id="table_1",
            source=SourceLocation(page_start=12, page_end=12),
            parser_metadata=ParserMetadata(parser_name="docling", extra={}),
        )
    )

    TableSemanticResolver().resolve(graph)

    table = graph.tables["table_1"]
    parser_extra = graph.elements["el_table_1"].parser_metadata.extra

    assert table.table_category == "maintenance_interval_table"
    assert table.table_shape == "maintenance_schedule_matrix"
    assert table.table_structure_quality is not None
    assert table.header_paths == [
        ["Task"],
        ["Interval", "Daily"],
        ["Interval", "Weekly"],
        ["Interval", "Monthly"],
    ]
    assert table.axis_summary["column_axis"] == "interval"
    assert parser_extra["table_shape"] == "maintenance_schedule_matrix"
    assert parser_extra["table_header_paths_json"] == [
        ["Task"],
        ["Interval", "Daily"],
        ["Interval", "Weekly"],
        ["Interval", "Monthly"],
    ]
    assert parser_extra["table_axis_summary"]["value_axis"] == "marker"
    assert table.signals == frozenset({"maintenance_intervals", "schedules"})
    assert parser_extra["table_signals"] == ["maintenance_intervals", "schedules"]


def test_table_semantic_resolver_persists_specification_matrix_metadata() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_2"] = TableAsset(
        table_id="table_2",
        document_id="doc_001",
        markdown="| Parameter | Compact version | Remote version | Unit |",
        rows=[
            ["Parameter", "Compact version", "Remote version", "Unit"],
            ["Pressure range", "0...10", "0...16", "bar"],
            ["Output signal", "4-20 mA", "4-20 mA", "mA"],
        ],
        row_count=3,
        column_count=4,
    )
    graph.add_element(
        CanonicalElement(
            element_id="el_table_2",
            document_id="doc_001",
            element_type=ElementType.TABLE,
            text="| Parameter | Compact version | Remote version | Unit |",
            table_id="table_2",
            source=SourceLocation(page_start=6, page_end=6),
            parser_metadata=ParserMetadata(parser_name="docling", extra={}),
        )
    )

    TableSemanticResolver().resolve(graph)

    table = graph.tables["table_2"]
    parser_extra = graph.elements["el_table_2"].parser_metadata.extra

    assert table.table_category in {
        "operating_limits_table",
        "technical_data_table",
    }
    assert table.table_shape == "specification_matrix"
    assert table.header_paths == [
        ["Parameter"],
        ["Field", "Compact version"],
        ["Field", "Remote version"],
        ["Unit"],
    ]
    assert table.axis_summary["row_axis"] == "parameter"
    assert parser_extra["table_shape"] == "specification_matrix"
    assert parser_extra["table_axis_summary"]["value_axis"] == "specification_value"


def test_table_semantic_resolver_persists_normalized_troubleshooting_rows() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_3"] = TableAsset(
        table_id="table_3",
        document_id="doc_001",
        markdown="troubleshooting",
        rows=[
            ["PROBLEM", "PROBABLE CAUSES", "", "POSSIBLE REMEDIES", ""],
            [
                "(6) Leakage from the mechanical seal",
                "6a)",
                "The mechanical seal has been",
                "6a)",
                "Replace the mechanical seal.",
            ],
            [
                "(6) Leakage from the mechanical seal",
                "6b)",
                "run dry or has stuck",
                "6b)",
                "Replace the mechanical seal.",
            ],
        ],
    )
    graph.add_element(
        CanonicalElement(
            element_id="el_table_3",
            document_id="doc_001",
            element_type=ElementType.TABLE,
            text="troubleshooting",
            table_id="table_3",
            source=SourceLocation(page_start=20, page_end=20),
            parser_metadata=ParserMetadata(parser_name="docling", extra={}),
        )
    )

    TableSemanticResolver().resolve(graph)

    table = graph.tables["table_3"]
    parser_extra = graph.elements["el_table_3"].parser_metadata.extra

    assert table.table_category == "troubleshooting_table"
    assert table.rows == [
        ["Symptom", "Cause", "Remedy"],
        [
            "(6) Leakage from the mechanical seal",
            "The mechanical seal has been run dry or has stuck",
            "Replace the mechanical seal.",
        ],
    ]
    assert parser_extra["table_rows"] == table.rows
    assert parser_extra["table_row_normalization_version"] == "1"
    assert parser_extra["row_count"] == 2
    assert parser_extra["column_count"] == 3


def test_table_semantic_resolver_persists_normalized_performance_curve_rows() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_4"] = TableAsset(
        table_id="table_4",
        document_id="doc_001",
        markdown="curve",
        rows=[
            ["Pump type", "Motor power", "Motor power", "Q m3/h", "0", "1", "1.5"],
            ["Pump type", "kW", "HP", "Q l/min", "0", "16.6", "25"],
            ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
        ],
    )
    graph.add_element(
        CanonicalElement(
            element_id="el_table_4",
            document_id="doc_001",
            element_type=ElementType.TABLE,
            text="curve",
            table_id="table_4",
            source=SourceLocation(page_start=30, page_end=30),
            parser_metadata=ParserMetadata(parser_name="docling", extra={}),
        )
    )

    TableSemanticResolver().resolve(graph)

    table = graph.tables["table_4"]
    parser_extra = graph.elements["el_table_4"].parser_metadata.extra

    assert table.table_category == "technical_data_table"
    assert table.table_shape == "performance_curve_matrix"
    assert table.rows == [
        [
            "Pump type",
            "Motor power (kW)",
            "Motor power (HP)",
            "Curve metric",
            "Q m3/h 0 / Q l/min 0",
            "Q m3/h 1 / Q l/min 16.6",
            "Q m3/h 1.5 / Q l/min 25",
        ],
        ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
    ]
    assert parser_extra["table_rows"] == table.rows
    assert parser_extra["table_row_normalization_version"] == "1"
