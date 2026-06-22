from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_marker_tuning import (
    StructuredFamilyMarkerTuning,
)
from src.application.workflows.parsing.builders.chunking.text.section_path_sanitizer import (
    sanitize_section_path,
)


def extend_markers(
    *,
    family: StructuredEvidenceFamily,
    base_markers: tuple[str, ...],
    marker_tuning: StructuredFamilyMarkerTuning | None,
) -> tuple[str, ...]:
    extras = (
        marker_tuning.extra_markers_for(family)
        if marker_tuning is not None
        else ()
    )
    return tuple(dict.fromkeys([*base_markers, *extras]))


def sanitized_base_path(
    *,
    section_path: list[str],
    section_title: str,
    document_title: str | None,
) -> list[str]:
    base_path = list(section_path) if section_path else [section_title]
    return sanitize_section_path(
        base_path,
        document_title=document_title,
    )


def append_label_if_missing(
    path: list[str],
    label: str,
) -> list[str]:
    if any(_normalize(part) == _normalize(label) for part in path):
        return path
    return [*path, label]


def path_contains_markers(
    path: list[str],
    markers: tuple[str, ...],
) -> bool:
    normalized_path = " > ".join(_normalize(part) for part in path if part)
    return any(marker in normalized_path for marker in markers)


def _normalize(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())
