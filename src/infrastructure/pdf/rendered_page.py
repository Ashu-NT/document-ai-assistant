from dataclasses import dataclass


@dataclass(slots=True)
class RenderedPage:
    pdf_path: str
    page_number: int
    image_path: str
    width: int
    height: int
    dpi: int

