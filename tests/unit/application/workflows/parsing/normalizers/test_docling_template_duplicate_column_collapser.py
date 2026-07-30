from src.application.workflows.parsing.normalizers.table_rows.docling_template_duplicate_column_collapser import (
    DoclingTemplateDuplicateColumnCollapser,
)


def test_collapse_removes_adjacent_duplicate_template_columns() -> None:
    rows = [
        [
            "Card of Task Specification",
            "Card of Task Specification",
            "Card of Task Specification",
        ],
        ["Location:", "Location:", "Machine Room"],
        ["Description of Task:", "Description of Task:", "Service main ropes"],
        ["1.", "1.", "Check rope tension"],
    ]

    collapsed = DoclingTemplateDuplicateColumnCollapser().collapse(rows)

    assert collapsed == [
        ["Card of Task Specification", "Card of Task Specification"],
        ["Location:", "Machine Room"],
        ["Description of Task:", "Service main ropes"],
        ["1.", "Check rope tension"],
    ]


def test_collapse_preserves_distinct_engineering_value_columns() -> None:
    rows = [
        ["Name", "Size", "Value"],
        ["Pump", "10 kW", "400 V"],
        ["Tank capacity", "1200 L", "1200 L"],
    ]

    collapsed = DoclingTemplateDuplicateColumnCollapser().collapse(rows)

    assert collapsed == rows
