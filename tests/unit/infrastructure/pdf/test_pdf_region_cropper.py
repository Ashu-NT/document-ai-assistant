from pathlib import Path

from src.domain.common import BoundingBox
from src.infrastructure.pdf import PDFRegionCropper


class FakeCroppedImage:
    def __init__(self) -> None:
        self.size = (100, 50)
        self.saved_paths: list[Path] = []

    def save(self, path: Path) -> None:
        self.saved_paths.append(path)


class FakeOpenedImage:
    def __init__(self) -> None:
        self.width = 400
        self.height = 200
        self.crop_calls: list[tuple[int, int, int, int]] = []
        self.cropped_image = FakeCroppedImage()

    def crop(self, box: tuple[int, int, int, int]) -> FakeCroppedImage:
        self.crop_calls.append(box)
        return self.cropped_image

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class FakeImageModule:
    def __init__(self, image: FakeOpenedImage) -> None:
        self.image = image
        self.calls: list[str] = []

    def open(self, image_path: str) -> FakeOpenedImage:
        self.calls.append(image_path)
        return self.image


def test_crop_uses_bbox_and_writes_output(monkeypatch, tmp_path) -> None:
    cropper = PDFRegionCropper()
    fake_image = FakeOpenedImage()
    fake_module = FakeImageModule(fake_image)
    monkeypatch.setattr(cropper, "_import_image_module", lambda: fake_module)

    result = cropper.crop(
        image_path="page.png",
        bbox=BoundingBox(x1=10, y1=20, x2=110, y2=70),
        output_dir=tmp_path,
    )

    assert fake_module.calls == ["page.png"]
    assert fake_image.crop_calls == [(10, 20, 110, 70)]
    assert Path(result.image_path).name == "page_crop.png"
    assert fake_image.cropped_image.saved_paths == [tmp_path / "page_crop.png"]
