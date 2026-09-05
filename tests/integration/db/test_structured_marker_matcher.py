import pytest

from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    StructuredMarkerMatcher,
)


@pytest.fixture
def matcher() -> StructuredMarkerMatcher:
    return StructuredMarkerMatcher()


def test_does_not_match_marker_inside_larger_word(
    matcher: StructuredMarkerMatcher,
) -> None:
    assert not matcher.contains(
        "reset to default settings",
        "fault",
    )

    assert not matcher.contains(
        "this provides a benefit",
        "fit",
    )


def test_matches_complete_single_word_marker(
    matcher: StructuredMarkerMatcher,
) -> None:
    assert matcher.contains(
        "a fault was detected",
        "fault",
    )

    assert matcher.contains(
        "fit the protective cover",
        "fit",
    )


def test_normalizes_punctuation_consistently(
    matcher: StructuredMarkerMatcher,
) -> None:
    assert matcher.contains(
        "Perform the start/run procedure.",
        "start/run",
    )

    assert matcher.contains(
        "Complete the pre-commissioning checks.",
        "pre-commissioning",
    )


def test_matches_multi_word_phrase(
    matcher: StructuredMarkerMatcher,
) -> None:
    assert matcher.contains(
        "Possible cause: insufficient supply pressure.",
        "possible cause",
    )


def test_does_not_match_partial_phrase(
    matcher: StructuredMarkerMatcher,
) -> None:
    assert not matcher.contains(
        "The default configuration is restored.",
        "fault",
    )