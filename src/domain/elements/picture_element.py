from dataclasses import dataclass

from src.domain.common import ElementType
from src.domain.elements.canonical_element import CanonicalElement


@dataclass(slots=True)
class PictureElement(CanonicalElement):
    caption: str | None = None

    def __init__(
        self,
        element_id: str,
        document_id: str,
        picture_id: str,
        caption: str | None = None,
        parent_section_id: str | None = None,
        reading_order: int | None = None,
    ) -> None:
        super().__init__(
            element_id=element_id,
            document_id=document_id,
            element_type=ElementType.PICTURE,
            text=caption,
            parent_section_id=parent_section_id,
            reading_order=reading_order,
            picture_id=picture_id,
        )
        self.caption = caption