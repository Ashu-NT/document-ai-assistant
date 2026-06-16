from dataclasses import dataclass

from src.domain.common import ElementType
from src.domain.elements.canonical_element import CanonicalElement


@dataclass(slots=True)
class TableElement(CanonicalElement):
    table_markdown: str | None = None

    def __init__(
        self,
        element_id: str,
        document_id: str,
        table_id: str,
        table_markdown: str | None = None,
        parent_section_id: str | None = None,
        reading_order: int | None = None,
    ) -> None:
        super().__init__(
            element_id=element_id,
            document_id=document_id,
            element_type=ElementType.TABLE,
            text=table_markdown,
            parent_section_id=parent_section_id,
            reading_order=reading_order,
            table_id=table_id,
        )
        self.table_markdown = table_markdown