from src.application.workflows.parsing.tables.semantics.table_structured_list_classifier import (
    TableStructuredListClassifier,
)


def _classifier() -> TableStructuredListClassifier:
    return TableStructuredListClassifier()


def test_looks_like_spare_parts_table_detects_the_plural_spare_parts_header() -> None:
    # Regression guard for a real bug: `TableTextSignalMatcher.contains` uses
    # whole-word padded matching, so a marker list containing only the
    # singular "spare part" never matches text containing only the plural
    # "spare parts" -- the exact same class of gap fixed earlier for
    # "year"/"years" at the maintenance-interval rule. Still requires a
    # second corroborating marker (here "qty"), same as the singular form
    # always has -- a single incidental "spare parts" mention alone (e.g. one
    # stray document with no other corroboration) is deliberately not enough.
    classifier = _classifier()
    headers = ["description extra spare parts", "qty"]
    direct_text = (
        "description extra spare parts qty "
        "360 500 3 4 barbed port 1200r 1 "
        "360 500 3 4 barbed port 90 degree 1201r 1"
    )
    assert classifier.looks_like_spare_parts_table(
        headers=headers,
        labels=[],
        body_rows=[],
        direct_text=direct_text,
        section_text="",
    )


def test_looks_like_spare_parts_table_still_detects_the_singular_header() -> None:
    classifier = _classifier()
    headers = ["spare part", "qty", "part no"]
    direct_text = "spare part qty part no gasket 1 a1234 seal ring 2 b5678"
    assert classifier.looks_like_spare_parts_table(
        headers=headers,
        labels=[],
        body_rows=[],
        direct_text=direct_text,
        section_text="",
    )
