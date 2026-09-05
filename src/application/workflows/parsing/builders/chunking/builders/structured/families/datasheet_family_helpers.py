from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    append_label_if_missing,
    path_contains_terms,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_context import (
    StructuredFamilyContext,
)


EMBEDDED_DATASHEET_REGION_MARKERS = (
    "datasheet",
    "product overview",
    "technical data",
    "technical features",
    "ordering information",
    "ordering example",
    "cooling system",
    "installation instructions",
    "operating limits",
    "pressure-temperature diagram",
    "pressure temperature diagram",
)


def family_section_path(
    *,
    base_path: list[str],
    family_markers: tuple[str, ...],
    label: str,
) -> list[str]:
    if path_contains_terms(
        base_path,
        family_markers,
    ):
        return base_path

    return append_label_if_missing(
        base_path,
        label,
    )


def has_embedded_datasheet_signal(
    context: StructuredFamilyContext,
) -> bool:
    return context.section_contains_any_term(
        EMBEDDED_DATASHEET_REGION_MARKERS
    ) or context.content_contains_any_term(
        EMBEDDED_DATASHEET_REGION_MARKERS
    )