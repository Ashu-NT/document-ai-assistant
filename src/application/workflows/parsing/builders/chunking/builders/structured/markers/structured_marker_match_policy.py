from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerMatch,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.structured_marker_matcher import (
    StructuredMarkerMatcher,
)


_NEGATED_AVAILABILITY_CUES = (
    "cannot be obtained as",
    "can not be obtained as",
    "not available as",
    "not obtainable as",
    "no longer available as",
    "not sold as",
    "not supplied as",
    "not offered as",
)


class StructuredMarkerMatchPolicy:
    """Applies contextual validity checks to structured marker matches."""

    def __init__(self, *, matcher: StructuredMarkerMatcher) -> None:
        self.matcher = matcher
        self.negation_cues = tuple(
            matcher.normalize(cue) for cue in _NEGATED_AVAILABILITY_CUES
        )

    def matches(self, text: str, markers: tuple[EvidenceMarker, ...]) -> bool:
        return bool(self.find_matches(text, markers))

    def find_matches(
        self,
        text: str,
        markers: tuple[EvidenceMarker, ...],
    ) -> tuple[MarkerMatch, ...]:
        normalized_text = self.matcher.normalize(text)
        accepted: list[MarkerMatch] = []
        for marker in markers:
            for match in self.matcher.iter_matches(normalized_text, marker):
                preceding_text = normalized_text[max(0, match.start - 80) : match.start]
                if any(cue in preceding_text for cue in self.negation_cues):
                    continue
                accepted.append(match)
        return tuple(accepted)
