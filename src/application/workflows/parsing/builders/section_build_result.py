from dataclasses import dataclass, field

from src.domain.document import DocumentSection


@dataclass(slots=True)
class SectionBuildResult:
    sections: list[DocumentSection]
    element_section_ids: dict[str, str] = field(default_factory=dict)
    element_section_paths: dict[str, list[str]] = field(default_factory=dict)
    header_levels: dict[str, int] = field(default_factory=dict)
    header_sources: dict[str, str] = field(default_factory=dict)
    header_raw_levels: dict[str, int | None] = field(default_factory=dict)
    header_section_ids: dict[str, str] = field(default_factory=dict)
