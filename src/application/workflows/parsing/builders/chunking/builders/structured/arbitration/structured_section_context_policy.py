from src.application.workflows.parsing.builders.chunking.builders.structured.markers.structured_marker_match_policy import (
    StructuredMarkerMatchPolicy,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.domain.document import DocumentSection


class StructuredSectionContextPolicy:
    """Determines whether a section locally owns an evidence family."""

    def __init__(self, *, marker_match_policy: StructuredMarkerMatchPolicy) -> None:
        self.marker_match_policy = marker_match_policy

    def matches_local_section(
        self,
        *,
        section: DocumentSection,
        spec: StructuredSectionWindowSpec,
    ) -> bool:
        local_labels = [section.title]
        if section.section_path:
            local_labels.append(section.section_path[-1])

        return any(
            self.marker_match_policy.matches(label, spec.anchor_markers)
            for label in dict.fromkeys(local_labels)
            if label
        )
