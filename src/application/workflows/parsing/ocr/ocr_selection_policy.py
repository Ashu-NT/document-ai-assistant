from dataclasses import dataclass


@dataclass(slots=True)
class OCRSelectionPolicy:
    asset_enabled: bool = True
    page_fallback_enabled: bool = False
    region_fallback_enabled: bool = False
    max_pages_per_document: int = 3
    max_regions_per_page: int = 2
    min_text_chars_per_page: int = 120
    min_text_density: float = 0.0025
    min_image_area_ratio: float = 0.35
    page_render_dpi: int = 150
    timeout_seconds: int = 30

