import pytest

from src.application.workflows.parsing.builders.chunking.builders.structured.markers.structured_marker_matcher import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)


@pytest.fixture
def matcher() -> StructuredMarkerMatcher:
    return StructuredMarkerMatcher()


def test_does_not_match_inside_larger_word(
    matcher: StructuredMarkerMatcher,
) -> None:
    fault = EvidenceMarker(
        text="fault",
        strength=MarkerStrength.WEAK,
    )

    assert not matcher.contains(
        "Reset to default settings.",
        fault,
    )


def test_fit_does_not_match_benefit(
    matcher: StructuredMarkerMatcher,
) -> None:
    fit = EvidenceMarker(
        text="fit",
        strength=MarkerStrength.WEAK,
    )

    assert not matcher.contains(
        "The primary benefit is reduced vibration.",
        fit,
    )


def test_matches_complete_word(
    matcher: StructuredMarkerMatcher,
) -> None:
    fault = EvidenceMarker(
        text="fault",
        strength=MarkerStrength.WEAK,
    )

    assert matcher.contains(
        "A fault was detected.",
        fault,
    )


def test_normalizes_marker_and_text_consistently(
    matcher: StructuredMarkerMatcher,
) -> None:
    marker = EvidenceMarker(
        text="pre-commissioning",
        strength=MarkerStrength.STRONG,
    )

    assert matcher.contains(
        "Complete the pre commissioning checks.",
        marker,
    )


def test_normalizes_slash_consistently(
    matcher: StructuredMarkerMatcher,
) -> None:
    marker = EvidenceMarker(
        text="start/run",
        strength=MarkerStrength.MEDIUM,
    )

    assert matcher.contains(
        "Follow the start/run procedure.",
        marker,
    )


def test_returns_diagnostic_match_information(
    matcher: StructuredMarkerMatcher,
) -> None:
    marker = EvidenceMarker(
        text="possible cause",
        strength=MarkerStrength.STRONG,
    )

    matches = matcher.find_matches(
        "Possible cause: insufficient pressure.",
        (marker,),
    )

    assert len(matches) == 1
    assert matches[0].marker == marker
    assert matches[0].start >= 0
    assert matches[0].end > matches[0].start