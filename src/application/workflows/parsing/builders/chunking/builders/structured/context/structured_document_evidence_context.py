from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
)


@dataclass(slots=True)
class StructuredDocumentEvidenceContext:
    """Document-level normalized evidence shared by every section."""

    normalized_title: str
    normalized_section_text: str
    matcher: StructuredMarkerMatcher = field(repr=False)
    _marker_presence: dict[tuple[str, ...], bool] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    @classmethod
    def build(
        cls,
        *,
        document_title: str | None,
        document_sections_combined_text: str,
        matcher: StructuredMarkerMatcher,
    ) -> "StructuredDocumentEvidenceContext":
        return cls(
            normalized_title=matcher.normalize(document_title),
            normalized_section_text=matcher.normalize(
                document_sections_combined_text
            ),
            matcher=matcher,
        )

    def contains_any(self, markers: tuple[EvidenceMarker, ...]) -> bool:
        cache_key = tuple(marker.text for marker in markers)
        cached = self._marker_presence.get(cache_key)
        if cached is not None:
            return cached

        found = self.matcher.contains_any_normalized(
            self.normalized_title,
            markers,
        ) or self.matcher.contains_any_normalized(
            self.normalized_section_text,
            markers,
        )
        self._marker_presence[cache_key] = found
        return found
