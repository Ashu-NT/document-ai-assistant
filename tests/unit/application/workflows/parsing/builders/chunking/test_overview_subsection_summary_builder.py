from src.application.workflows.parsing.builders.chunking.builders.overview.overview_subsection_summary_builder import (
    OverviewSubsectionSummaryBuilder,
)


def _word_count_tokens(text: str) -> int:
    return len(text.split())


def test_build_returns_none_for_empty_titles() -> None:
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    result = builder.build([], max_tokens=100)

    assert result is None


def test_build_returns_none_when_max_tokens_is_zero_or_negative() -> None:
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    assert builder.build(["Filter replacement"], max_tokens=0) is None
    assert builder.build(["Filter replacement"], max_tokens=-5) is None


def test_build_produces_full_summary_with_exact_count_and_titles() -> None:
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    result = builder.build(
        ["Filter replacement", "Oil change"],
        max_tokens=100,
    )

    assert result == "Direct subsections (2): Filter replacement; Oil change"


def test_build_reports_total_count_even_when_only_one_title() -> None:
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    result = builder.build(["Introduction"], max_tokens=100)

    assert result == "Direct subsections (1): Introduction"


def test_build_truncates_to_a_partial_title_list_when_full_summary_overflows() -> None:
    # count_tokens is called with the whole candidate string each time, so
    # the budget has to cover "Direct subsections (N): " plus the included
    # titles plus the "[K omitted...]" suffix -- not just the raw title text.
    titles = [f"Subsection {i}" for i in range(10)]
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    result = builder.build(titles, max_tokens=12)

    assert result is not None
    assert result.startswith("Direct subsections (10):")
    assert "omitted due to token limit" in result
    assert _word_count_tokens(result) <= 12


def test_build_falls_back_to_count_only_summary_when_even_one_title_overflows() -> None:
    # A single-title list skips the per-title omission loop entirely (its
    # range is empty when total == 1), so an overflowing full summary must
    # fall straight through to the titleless, honest count-only line.
    titles = ["A very long subsection title that will not fit in a tiny budget"]
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    result = builder.build(titles, max_tokens=10)

    assert result == "Direct subsections: 1 total; titles omitted due to token limit."


def test_build_returns_none_when_even_the_count_only_summary_overflows() -> None:
    titles = ["A very long subsection title that will not fit in a tiny budget"]
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    result = builder.build(titles, max_tokens=9)

    assert result is None


def test_build_uses_semicolon_separator_between_titles() -> None:
    builder = OverviewSubsectionSummaryBuilder(count_tokens=_word_count_tokens)

    result = builder.build(["First", "Second", "Third"], max_tokens=100)

    assert result == "Direct subsections (3): First; Second; Third"
