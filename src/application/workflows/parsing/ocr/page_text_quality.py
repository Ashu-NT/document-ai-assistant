from dataclasses import dataclass, field


@dataclass(slots=True)
class PageTextQuality:
    page_number: int
    text_char_count: int
    word_count: int
    element_count: int
    table_count: int
    image_count: int
    text_density: float | None = None
    image_area_ratio: float | None = None
    has_text: bool = False
    is_text_poor: bool = False
    is_probably_scanned: bool = False
    replacement_char_count: int = 0
    has_corrupted_text: bool = False
    reasons: list[str] = field(default_factory=list)

