from src.application.workflows.parsing.tables.table_header_compatibility_matcher import (
    TableHeaderCompatibilityMatcher,
)
from src.domain.assets import TableAsset


def test_unrelated_tables_with_different_umbrella_titles_are_not_compatible() -> None:
    """Regression test: two unrelated tables that merely share a generic
    deeper header (e.g. "Parameter | Value") but have different umbrella
    titles must not be treated as continuations of the same table.
    """
    table_a = TableAsset(
        table_id="t1",
        document_id="d1",
        markdown="x",
        rows=[
            ["Motor Specifications", "Motor Specifications"],
            ["Parameter", "Value"],
            ["Voltage", "400V"],
        ],
    )
    table_b = TableAsset(
        table_id="t2",
        document_id="d1",
        markdown="x",
        rows=[
            ["Pump Specifications", "Pump Specifications"],
            ["Parameter", "Value"],
            ["Flow rate", "50 m3/h"],
        ],
    )

    assert TableHeaderCompatibilityMatcher().are_compatible(table_a, table_b) is False


def test_continuation_pages_with_minor_umbrella_variation_are_compatible() -> None:
    """A repeated umbrella title with only a trailing page-number-style
    variation (a common continuation-page artifact) should still match
    when the deeper headers are identical.
    """
    table_a = TableAsset(
        table_id="t1",
        document_id="d1",
        markdown="x",
        rows=[
            ["Maintenance Schedule (1 of 2)", "Maintenance Schedule (1 of 2)"],
            ["Task", "Notes"],
            ["Check oil", "See annex"],
        ],
    )
    table_b = TableAsset(
        table_id="t2",
        document_id="d1",
        markdown="x",
        rows=[
            ["Maintenance Schedule (2 of 2)", "Maintenance Schedule (2 of 2)"],
            ["Task", "Notes"],
            ["Replace filter", "Use OEM part"],
        ],
    )

    assert TableHeaderCompatibilityMatcher().are_compatible(table_a, table_b) is True


def test_same_simple_header_without_umbrella_is_still_compatible() -> None:
    table_a = TableAsset(
        table_id="t1",
        document_id="d1",
        markdown="x",
        rows=[["Parameter", "Value"], ["Voltage", "400V"]],
    )
    table_b = TableAsset(
        table_id="t2",
        document_id="d1",
        markdown="x",
        rows=[["Parameter", "Value"], ["Current", "12A"]],
    )

    assert TableHeaderCompatibilityMatcher().are_compatible(table_a, table_b) is True
