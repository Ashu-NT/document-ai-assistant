from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    GENERIC_STRUCTURED_MARKERS,
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
)


class StructuredSignalDetector:
    def __init__(
        self,
        *,
        markers: tuple[EvidenceMarker, ...] | None = None,
        marker_matcher: StructuredMarkerMatcher | None = None,
    ) -> None:
        self.markers = markers or GENERIC_STRUCTURED_MARKERS
        self.marker_matcher = marker_matcher or StructuredMarkerMatcher()

    def has_structured_markers(
        self,
        *,
        document_title: str | None,
        values: list[str],
    ) -> bool:
        _ = document_title

        return any(
            self.marker_matcher.contains_any(
                value,
                self.markers,
            )
            for value in values
            if value
        )