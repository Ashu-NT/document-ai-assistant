from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.chunking.builders.structured.spec.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)


@dataclass(slots=True, frozen=True)
class StructuredFamilySpecSelection:
    specs: list[StructuredSectionWindowSpec] = field(default_factory=list)
