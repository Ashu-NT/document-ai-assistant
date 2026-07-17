from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
    TableShapeResolver,
)
from src.domain.assets import TableAsset


def test_shape_resolver_prefers_declared_shape() -> None:
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="unused",
        table_shape="maintenance_schedule_matrix",
        rows=[["Task", "D"], ["Inspect", "x"]],
    )

    assert TableShapeResolver().resolve(table) == "maintenance_schedule_matrix"


def test_shape_resolver_detects_performance_curve_matrix() -> None:
    table = TableAsset(
        table_id="table_006",
        document_id="doc_001",
        markdown="unused",
        rows=[
            [
                "Pump type",
                "Motor power",
                "Motor power",
                "Q m3/h",
                "0",
                "1",
                "1.5",
            ],
            [
                "Pump type",
                "kW",
                "HP",
                "Q l/min",
                "0",
                "16.6",
                "25",
            ],
            ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
        ],
    )

    assert TableShapeResolver().resolve(table) == "performance_curve_matrix"


def test_shape_resolver_returns_none_without_known_shape() -> None:
    table = TableAsset(
        table_id="table_003",
        document_id="doc_001",
        markdown="unused",
        rows=[["Part Number", "Description"], ["HP-001", "Filter"]],
    )

    assert TableShapeResolver().resolve(table) is None
