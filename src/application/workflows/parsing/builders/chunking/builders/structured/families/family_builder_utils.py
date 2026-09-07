from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_marker_tuning import (
    StructuredFamilyMarkerTuning,
)
from src.application.workflows.parsing.builders.chunking.text.section_path_sanitizer import (
    sanitize_section_path,
)


_MARKER_MATCHER = StructuredMarkerMatcher()


def extend_markers(
    *,
    family: StructuredEvidenceFamily,
    base_markers: tuple[EvidenceMarker, ...],
    marker_tuning: StructuredFamilyMarkerTuning | None,
) -> tuple[EvidenceMarker, ...]:
    extras = (
        marker_tuning.extra_markers_for(family)
        if marker_tuning is not None
        else ()
    )

    merged: list[EvidenceMarker] = []
    seen: set[str] = set()

    for marker in (*base_markers, *extras):
        normalized = _MARKER_MATCHER.normalize(marker.text)

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        merged.append(marker)

    return tuple(merged)


def sanitized_base_path(
    *,
    section_path: list[str],
    section_title: str,
    document_title: str | None,
) -> list[str]:
    base_path = (
        list(section_path)
        if section_path
        else [section_title]
    )

    return sanitize_section_path(
        base_path,
        document_title=document_title,
    )


def append_label_if_missing(
    path: list[str],
    label: str,
) -> list[str]:
    normalized_label = _MARKER_MATCHER.normalize(label)

    if any(
        _MARKER_MATCHER.normalize(part) == normalized_label
        for part in path
    ):
        return path

    return [*path, label]


def path_contains_markers(
    path: list[str],
    markers: tuple[EvidenceMarker, ...],
) -> bool:
    path_text = " > ".join(
        part
        for part in path
        if part
    )

    return _MARKER_MATCHER.contains_any(
        path_text,
        markers,
    )
    
def path_contains_terms(
    path: list[str],
    terms: tuple[str, ...],
) -> bool:
    path_text = " > ".join(
        part
        for part in path
        if part
    )

    return _MARKER_MATCHER.contains_any_term(
        path_text,
        terms,
    )