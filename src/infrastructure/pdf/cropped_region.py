from dataclasses import dataclass

from src.domain.common import BoundingBox


@dataclass(slots=True)
class CroppedRegion:
    source_image_path: str
    image_path: str
    bbox: BoundingBox
    width: int
    height: int

