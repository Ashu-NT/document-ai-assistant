from src.application.workflows.parsing.tables.structure.compact_interval_header_token_matcher import (
    CompactIntervalHeaderTokenMatcher,
)


def test_matches_bare_schedule_code_letters() -> None:
    matcher = CompactIntervalHeaderTokenMatcher()

    for token in ["d", "w", "m", "q", "s", "a"]:
        assert matcher.matches(token) is True


def test_matches_full_schedule_words_case_insensitively() -> None:
    matcher = CompactIntervalHeaderTokenMatcher()

    for token in ["Daily", "WEEKLY", "Monthly", "quarterly", "Annual", "Annually", "Yearly"]:
        assert matcher.matches(token) is True


def test_matches_semi_annual_with_or_without_hyphen() -> None:
    matcher = CompactIntervalHeaderTokenMatcher()

    assert matcher.matches("semi-annual") is True
    assert matcher.matches("semi annual") is True


def test_strips_surrounding_whitespace() -> None:
    matcher = CompactIntervalHeaderTokenMatcher()

    assert matcher.matches("  d  ") is True


def test_rejects_unrelated_tokens() -> None:
    matcher = CompactIntervalHeaderTokenMatcher()

    assert matcher.matches("task") is False
    assert matcher.matches("") is False
    assert matcher.matches("Ad") is False


def test_rejects_tokens_that_only_partially_match() -> None:
    matcher = CompactIntervalHeaderTokenMatcher()

    assert matcher.matches("daily inspection") is False
