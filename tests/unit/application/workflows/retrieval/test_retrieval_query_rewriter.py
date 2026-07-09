from src.application.workflows.retrieval.retrieval_query_rewriter import (
    RetrievalQueryRewriter,
)

rewriter = RetrievalQueryRewriter()


def test_rewrite_expands_lowercase_abbreviation() -> None:
    assert rewriter.rewrite("What is part no. 123?") == "What is part number 123?"


def test_rewrite_expands_capitalized_abbreviation() -> None:
    """Case-sensitivity regression guard: the original implementation used
    a plain str.replace() against lowercase source strings, so capitalized
    input like 'Part No.' silently never expanded."""
    assert rewriter.rewrite("What is Part No. 123?") == "What is part number 123?"


def test_rewrite_expands_uppercase_abbreviation() -> None:
    assert rewriter.rewrite("What is PART NO. 123?") == "What is part number 123?"


def test_rewrite_expands_serial_number_slash_abbreviation() -> None:
    assert rewriter.rewrite("What is S/N 456?") == "What is serial number 456?"


def test_rewrite_normalizes_unicode_dashes() -> None:
    assert rewriter.rewrite("Torque range 10–20 Nm") == "Torque range 10-20 Nm"


def test_rewrite_returns_none_when_nothing_changes() -> None:
    assert rewriter.rewrite("What is the operating pressure?") is None


def test_rewrite_returns_none_for_empty_text() -> None:
    assert rewriter.rewrite("") is None


def test_rewrite_collapses_extra_whitespace_alongside_abbreviation_expansion() -> None:
    assert rewriter.rewrite("What   is  part no.   123?") == "What is part number 123?"


def test_rewrite_collapses_extra_whitespace_even_with_no_abbreviation_match() -> None:
    """Whitespace normalization alone counts as a change (matches the
    original: the whitespace-collapsed result differs from the raw input,
    so it's returned rather than None)."""
    assert rewriter.rewrite("What   is  the  pressure?") == "What is the pressure?"
