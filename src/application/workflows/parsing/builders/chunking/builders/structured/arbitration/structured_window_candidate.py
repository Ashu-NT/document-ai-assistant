from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.domain.elements import CanonicalElement


@dataclass(frozen=True, slots=True)
class StructuredWindowCandidate:
    spec: StructuredSectionWindowSpec
    elements: tuple[CanonicalElement, ...]
    anchor_element_ids: frozenset[str]
    score: int
    direct_evidence: bool
    reference_only: bool = False

    @property
    def element_ids(self) -> frozenset[str]:
        return frozenset(element.element_id for element in self.elements)

    @property
    def order_index(self) -> int:
        if not self.elements:
            return 0
        return self.elements[0].reading_order or 0
