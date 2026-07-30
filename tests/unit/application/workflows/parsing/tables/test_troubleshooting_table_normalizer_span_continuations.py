from src.application.workflows.parsing.tables.normalization.troubleshooting.troubleshooting_table_normalizer import (
    TroubleshootingTableNormalizer,
)
from src.domain.assets.table_cell_span import TableCellSpan


def test_normalize_merges_troubleshooting_rows_from_span_evidence() -> None:
    rows = [
        ["PROBLEM", "POSSIBLE CAUSES", "POSSIBLE REMEDIES"],
        ["(1) Pump stopped", "Control panel shows", "Check controller settings"],
        ["(1) Pump stopped", "No Signal Available", "Check controller settings"],
    ]

    normalized = TroubleshootingTableNormalizer().normalize(
        rows,
        table_category="troubleshooting_table",
        chunk_type=None,
        cell_spans=[
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=1,
                col_end=1,
                text="Control panel shows No Signal Available",
                raw_lines=["Control panel shows", "No Signal Available"],
            )
        ],
    )

    assert normalized is not None
    assert normalized.headers == ["Symptom", "Cause", "Remedy"]
    assert normalized.rows == [
        [
            "(1) Pump stopped",
            "Control panel shows No Signal Available",
            "Check controller settings",
        ]
    ]


def test_normalize_does_not_merge_troubleshooting_rows_without_span_evidence() -> None:
    rows = [
        ["PROBLEM", "POSSIBLE CAUSES", "POSSIBLE REMEDIES"],
        ["(1) Pump stopped", "Control panel shows", "Check controller settings"],
        ["(1) Pump stopped", "No Signal Available", "Check controller settings"],
    ]

    normalized = TroubleshootingTableNormalizer().normalize(
        rows,
        table_category="troubleshooting_table",
        chunk_type=None,
        cell_spans=None,
    )

    assert normalized is not None
    assert normalized.rows == [
        [
            "(1) Pump stopped",
            "Control panel shows",
            "Check controller settings",
        ],
        [
            "(1) Pump stopped",
            "No Signal Available",
            "Check controller settings",
        ],
    ]
