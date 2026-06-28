from pathlib import Path

from src.domain.common import BoundingBox
from src.infrastructure.pdf.cropped_region import CroppedRegion
from src.shared.exceptions import InfrastructureError


class PDFRegionCropper:
    def crop(
        self,
        image_path: str,
        bbox: BoundingBox,
        output_dir: str | Path,
    ) -> CroppedRegion:
        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = output_directory / f"{Path(image_path).stem}_crop.png"

        try:
            image_module = self._import_image_module()
            with image_module.open(image_path) as image:
                crop_box = self._resolve_crop_box(
                    bbox=bbox,
                    image_width=image.width,
                    image_height=image.height,
                )
                if crop_box is None:
                    raise InfrastructureError(
                        "OCR region crop box is invalid after clipping.",
                        details={
                            "image_path": image_path,
                            "bbox": {
                                "x1": bbox.x1,
                                "y1": bbox.y1,
                                "x2": bbox.x2,
                                "y2": bbox.y2,
                            },
                        },
                    )

                cropped = image.crop(crop_box)
                cropped.save(output_path)
                width, height = cropped.size

            return CroppedRegion(
                source_image_path=image_path,
                image_path=str(output_path),
                bbox=bbox,
                width=width,
                height=height,
            )
        except InfrastructureError:
            raise
        except Exception as exc:
            raise InfrastructureError(
                "Failed to crop OCR region from rendered page image.",
                details={"image_path": image_path},
            ) from exc

    @classmethod
    def _resolve_crop_box(
        cls,
        *,
        bbox: BoundingBox,
        image_width: int,
        image_height: int,
    ) -> tuple[int, int, int, int] | None:
        x1, y1, x2, y2 = cls._resolve_coordinates(
            bbox=bbox,
            image_width=image_width,
            image_height=image_height,
        )

        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        x1 = max(0, min(image_width, x1))
        x2 = max(0, min(image_width, x2))
        y1 = max(0, min(image_height, y1))
        y2 = max(0, min(image_height, y2))

        if x2 <= x1 or y2 <= y1:
            return None

        return (x1, y1, x2, y2)

    @staticmethod
    def _resolve_coordinates(
        *,
        bbox: BoundingBox,
        image_width: int,
        image_height: int,
    ) -> tuple[int, int, int, int]:
        values = (bbox.x1, bbox.y1, bbox.x2, bbox.y2)
        if all(0.0 <= value <= 1.0 for value in values):
            return (
                round(bbox.x1 * image_width),
                round(bbox.y1 * image_height),
                round(bbox.x2 * image_width),
                round(bbox.y2 * image_height),
            )

        return (
            round(bbox.x1),
            round(bbox.y1),
            round(bbox.x2),
            round(bbox.y2),
        )

    @staticmethod
    def _import_image_module():
        from PIL import Image

        return Image

