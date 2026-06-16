from dataclasses import dataclass

from src.domain.common import ElementType
from src.domain.elements.canonical_element import CanonicalElement


@dataclass(slots=True)
class FormulaElement(CanonicalElement):
    latex: str | None = None

    def __init__(
        self,
        element_id: str,
        document_id: str,
        latex: str | None = None,
        text: str | None = None,
        parent_section_id: str | None = None,
        reading_order: int | None = None,
    ) -> None:
        super().__init__(
            element_id=element_id,
            document_id=document_id,
            element_type=ElementType.FORMULA,
            text=text or latex,
            parent_section_id=parent_section_id,
            reading_order=reading_order,
        )
        self.latex = latex