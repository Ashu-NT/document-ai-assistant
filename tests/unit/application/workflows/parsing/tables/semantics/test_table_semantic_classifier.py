from src.application.workflows.parsing.tables.semantics import (
    TableCategory,
    TableSemanticClassifier,
)
from src.domain.assets import TableAsset


def _make_table(rows: list[list[str]], *, markdown: str = "table") -> TableAsset:
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown=markdown,
        rows=rows,
        row_count=len(rows),
        column_count=len(rows[0]) if rows else None,
    )


def test_classify_detects_generic_maintenance_interval_matrix() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Task", "Daily", "Weekly", "Monthly"],
                ["Inspect filter", "x", "", "x"],
            ]
        ),
    )

    assert category == TableCategory.MAINTENANCE_INTERVAL_TABLE
    assert confidence >= 0.9


def test_classify_detects_troubleshooting_table() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Symptom", "Possible cause", "Corrective action"],
                ["Low pressure", "Blocked filter", "Clean filter"],
            ]
        ),
    )

    assert category == TableCategory.TROUBLESHOOTING_TABLE
    assert confidence >= 0.9


def test_classify_detects_technical_data_table() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Parameter", "Value"],
                ["Voltage", "24 V"],
                ["Power", "5 kW"],
            ]
        ),
    )

    assert category == TableCategory.TECHNICAL_DATA_TABLE
    assert confidence >= 0.8


def test_classify_detects_toc_table_from_item_label() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table([["1", "Introduction", "2"]]),
        item_label="document_index",
    )

    assert category == TableCategory.TOC_TABLE
    assert confidence >= 0.99
