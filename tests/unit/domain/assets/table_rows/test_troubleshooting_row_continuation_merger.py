from src.application.workflows.parsing.tables.normalization.troubleshooting_row_continuation_merger import (
    TroubleshootingRowContinuationMerger,
)


def test_merges_adjacent_wrapped_cause_rows_for_the_same_issue() -> None:
    merged = TroubleshootingRowContinuationMerger().merge(
        headers=["Symptom", "Cause", "Remedy"],
        rows=[
            [
                "(6) Leakage from the mechanical seal",
                "The mechanical seal has been",
                "Replace the mechanical seal.",
            ],
            [
                "(6) Leakage from the mechanical seal",
                "run dry or has stuck",
                "Replace the mechanical seal.",
            ],
            [
                "(6) Leakage from the mechanical seal",
                "Slight initial drip during filling or on first start-up.",
                "Replace the mechanical seal.",
            ],
        ],
    )

    assert merged == [
        [
            "(6) Leakage from the mechanical seal",
            "The mechanical seal has been run dry or has stuck",
            "Replace the mechanical seal.",
        ],
        [
            "(6) Leakage from the mechanical seal",
            "Slight initial drip during filling or on first start-up.",
            "Replace the mechanical seal.",
        ],
    ]


def test_does_not_merge_distinct_complete_causes_with_the_same_remedy() -> None:
    merged = TroubleshootingRowContinuationMerger().merge(
        headers=["Symptom", "Cause", "Remedy"],
        rows=[
            ["Pump does not start", "No power supply", "Check power supply."],
            ["Pump does not start", "Shaft locked", "Check power supply."],
        ],
    )

    assert merged == [
        ["Pump does not start", "No power supply", "Check power supply."],
        ["Pump does not start", "Shaft locked", "Check power supply."],
    ]
