import re

from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    MarkerMatch,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.structured_marker_matcher import (
    StructuredMarkerMatcher,
)


_REFERENCE_CUE_PATTERN = re.compile(
    r"\b(?:see|refer(?:red)?\s+to|consult|according\s+to|in\s+accordance\s+with|"
    r"specified\s+in|described\s+in|listed\s+in|shown\s+in|documented\s+in|"
    r"contained\s+in|provided\s+in|found\s+in|in\s+the\s+appendix)\b"
)


class StructuredReferenceEvidencePolicy:
    """Distinguishes evidence from prose that only points to other evidence."""

    def __init__(self, *, matcher: StructuredMarkerMatcher) -> None:
        self.matcher = matcher

    def is_reference_only(
        self,
        text: str,
        matches: tuple[MarkerMatch, ...],
    ) -> bool:
        if not matches:
            return False

        normalized = self.matcher.normalize(text)
        return all(
            self._match_is_reference(normalized, match)
            for match in matches
        )

    @staticmethod
    def _match_is_reference(text: str, match: MarkerMatch) -> bool:
        context_start = max(0, match.start - 90)
        context_end = min(len(text), match.end + 90)
        context = text[context_start:context_end]
        return _REFERENCE_CUE_PATTERN.search(context) is not None
