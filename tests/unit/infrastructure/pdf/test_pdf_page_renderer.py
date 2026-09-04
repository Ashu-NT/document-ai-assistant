from pathlib import Path

import pytest

from src.infrastructure.pdf import PDFPageRenderer
from src.infrastructure.pdf.pdfium_process_lock import PDFIUM_PROCESS_LOCK
from src.shared.exceptions import InfrastructureError


class FakeImage:
    def __init__(self) -> None:
        self.size = (640, 480)
        self.saved_paths: list[Path] = []

    def save(self, path: Path) -> None:
        self.saved_paths.append(path)


class FakeBitmap:
    def __init__(self, image: FakeImage) -> None:
        self.image = image

    def to_pil(self) -> FakeImage:
        return self.image


class FakePage:
    def __init__(self, bitmap: FakeBitmap) -> None:
        self.bitmap = bitmap

    def render(self, scale: float):
        assert scale == pytest.approx(2.0)
        return self.bitmap

    def close(self) -> None:
        return None


class FakeDocument:
    def __init__(self, page: FakePage) -> None:
        self.page = page

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int) -> FakePage:
        assert index == 0
        return self.page

    def close(self) -> None:
        return None


class FakePdfiumModule:
    def __init__(self, document: FakeDocument) -> None:
        self.document = document

    def PdfDocument(self, pdf_path: str) -> FakeDocument:
        assert pdf_path == "manual.pdf"
        return self.document


def test_render_page_creates_rendered_page(monkeypatch, tmp_path) -> None:
    renderer = PDFPageRenderer()
    image = FakeImage()
    fake_module = FakePdfiumModule(
        FakeDocument(
            FakePage(FakeBitmap(image))
        )
    )
    monkeypatch.setattr(renderer, "_import_pypdfium2", lambda: fake_module)

    result = renderer.render_page(
        pdf_path="manual.pdf",
        page_number=1,
        dpi=144,
        output_dir=tmp_path,
    )

    assert result.pdf_path == "manual.pdf"
    assert result.page_number == 1
    assert result.width == 640
    assert result.height == 480
    assert Path(result.image_path).name == "manual_page_1.png"
    assert image.saved_paths == [tmp_path / "manual_page_1.png"]


def test_render_page_rejects_invalid_page_number(tmp_path) -> None:
    renderer = PDFPageRenderer()

    with pytest.raises(InfrastructureError):
        renderer.render_page(
            pdf_path="manual.pdf",
            page_number=0,
            dpi=144,
            output_dir=tmp_path,
        )


def test_render_page_acquires_the_shared_pdfium_process_lock(monkeypatch, tmp_path) -> None:
    """Regression: PDFPageRenderer and PdfLinkAnnotationExtractor share one
    process-wide lock (see pdfium_process_lock.py) - a lock scoped only to
    the new extractor would not prevent a future scenario where this
    renderer and the extractor ran on two threads of the same process at
    once."""
    lock_observations: list[bool] = []
    image = FakeImage()

    class ObservingPage(FakePage):
        def render(self, scale: float):
            lock_observations.append(PDFIUM_PROCESS_LOCK.locked())
            return super().render(scale)

    class ObservingDocument(FakeDocument):
        pass

    class ObservingPdfiumModule:
        def __init__(self, document) -> None:
            self.document = document

        def PdfDocument(self, pdf_path: str):
            lock_observations.append(PDFIUM_PROCESS_LOCK.locked())
            return self.document

    renderer = PDFPageRenderer()
    fake_module = ObservingPdfiumModule(
        ObservingDocument(ObservingPage(FakeBitmap(image)))
    )
    monkeypatch.setattr(renderer, "_import_pypdfium2", lambda: fake_module)

    renderer.render_page(
        pdf_path="manual.pdf",
        page_number=1,
        dpi=144,
        output_dir=tmp_path,
    )

    assert lock_observations, "no pdfium call was observed"
    assert all(lock_observations)
    assert not PDFIUM_PROCESS_LOCK.locked()
