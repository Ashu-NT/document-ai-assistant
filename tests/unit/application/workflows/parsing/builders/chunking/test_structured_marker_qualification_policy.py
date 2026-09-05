import pytest

from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerMatch,
    MarkerQualificationReason,
    MarkerStrength,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.qualification_policy import (
    StructuredMarkerQualificationPolicy,
)


@pytest.fixture
def policy() -> StructuredMarkerQualificationPolicy:
    return StructuredMarkerQualificationPolicy()


def match(
    text: str,
    strength: MarkerStrength,
    start: int = 0,
) -> MarkerMatch:
    marker = EvidenceMarker(
        text=text,
        strength=strength,
    )

    return MarkerMatch(
        marker=marker,
        start=start,
        end=start + len(text),
    )
    
def test_strong_marker_qualifies(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    result = policy.qualify(
        matches=(
            match(
                "possible cause",
                MarkerStrength.STRONG,
            ),
        ),
    )

    assert result.qualified
    assert result.score == 4
    assert result.reason == MarkerQualificationReason.STRONG_MARKER
    
def test_single_medium_marker_is_insufficient(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    result = policy.qualify(
        matches=(
            match(
                "low flow",
                MarkerStrength.MEDIUM,
            ),
        ),
    )

    assert not result.qualified
    assert result.score == 2
    
def test_two_medium_markers_qualify(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    result = policy.qualify(
        matches=(
            match("low flow", MarkerStrength.MEDIUM),
            match("reduced speed", MarkerStrength.MEDIUM),
        ),
    )

    assert result.qualified
    assert result.score == 4
    
def test_medium_marker_with_section_context_qualifies(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    result = policy.qualify(
        matches=(
            match(
                "low flow",
                MarkerStrength.MEDIUM,
            ),
        ),
        section_context_matches=True,
    )

    assert result.qualified
    assert result.score == 4
    
    
def test_single_weak_marker_with_context_is_still_insufficient(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    result = policy.qualify(
        matches=(
            match(
                "fault",
                MarkerStrength.WEAK,
            ),
        ),
        section_context_matches=True,
    )

    assert not result.qualified
    assert result.score == 3
    
def test_two_weak_markers_with_context_qualify(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    result = policy.qualify(
        matches=(
            match("fault", MarkerStrength.WEAK),
            match("leakage", MarkerStrength.WEAK),
        ),
        section_context_matches=True,
    )

    assert result.qualified
    assert result.score == 4
    
def test_weak_only_evidence_without_context_is_rejected(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    result = policy.qualify(
        matches=(
            match("warning", MarkerStrength.WEAK),
            match("hazard", MarkerStrength.WEAK),
            match("safety", MarkerStrength.WEAK),
            match("precaution", MarkerStrength.WEAK),
        ),
        section_context_matches=False,
    )

    assert not result.qualified
    assert (
        result.reason
        == MarkerQualificationReason.WEAK_ONLY_WITHOUT_CONTEXT
    )
    
def test_repeated_same_marker_does_not_inflate_score(
    policy: StructuredMarkerQualificationPolicy,
) -> None:
    marker = EvidenceMarker(
        "fault",
        MarkerStrength.WEAK,
    )

    result = policy.qualify(
        matches=(
            MarkerMatch(marker, 0, 5),
            MarkerMatch(marker, 20, 25),
            MarkerMatch(marker, 40, 45),
        ),
    )

    assert result.evidence.weak_count == 1
    assert result.score == 1
    assert not result.qualified