from pathlib import Path
from typing import Any

from src.infrastructure.pdf.rendered_page import RenderedPage
from src.shared.exceptions import InfrastructureError


def _validate_page_render_args(*, page_number: int, dpi: int) -> None:
    if page_number < 1:
        raise InfrastructureError(
            "PDF page rendering requires a 1-based page number.",
            details={"page_number": page_number},
        )
    if dpi <= 0:
        raise InfrastructureError(
            "PDF page rendering requires a positive DPI.",
            details={"dpi": dpi},
        )


class OpenedPDFDocument:
    """Keeps one pypdfium2 PdfDocument open across multiple render_page()
    calls, so callers rendering several pages of the same PDF (e.g. OCR
    fallback processing multiple page/region targets) only pay the
    file-open + structure-parse cost once instead of once per page."""

    def __init__(self, *, pdf_path: str, document: Any) -> None:
        self.pdf_path = pdf_path
        self.document = document

    def render_page(
        self,
        page_number: int,
        dpi: int,
        output_dir: str | Path,
    ) -> RenderedPage:
        _validate_page_render_args(page_number=page_number, dpi=dpi)

        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = (
            output_directory / f"{Path(self.pdf_path).stem}_page_{page_number}.png"
        )

        page = None
        try:
            page_index = page_number - 1
            if page_index >= len(self.document):
                raise InfrastructureError(
                    "Requested page number exceeds the PDF page count.",
                    details={
                        "pdf_path": self.pdf_path,
                        "page_number": page_number,
                        "page_count": len(self.document),
                    },
                )

            page = self.document[page_index]
            bitmap = page.render(scale=dpi / 72.0)
            image = bitmap.to_pil()
            image.save(output_path)
            width, height = image.size
            return RenderedPage(
                pdf_path=self.pdf_path,
                page_number=page_number,
                image_path=str(output_path),
                width=width,
                height=height,
                dpi=dpi,
            )
        except InfrastructureError:
            raise
        except Exception as exc:
            raise InfrastructureError(
                "Failed to render PDF page.",
                details={
                    "pdf_path": self.pdf_path,
                    "page_number": page_number,
                    "dpi": dpi,
                },
            ) from exc
        finally:
            PDFPageRenderer._safe_close(page)

    def close(self) -> None:
        PDFPageRenderer._safe_close(self.document)

    def __enter__(self) -> "OpenedPDFDocument":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


class PDFPageRenderer:
    def open(self, pdf_path: str) -> OpenedPDFDocument:
        pdfium = self._import_pypdfium2()
        document = pdfium.PdfDocument(pdf_path)
        return OpenedPDFDocument(pdf_path=pdf_path, document=document)

    def render_page(
        self,
        pdf_path: str,
        page_number: int,
        dpi: int,
        output_dir: str | Path,
    ) -> RenderedPage:
        _validate_page_render_args(page_number=page_number, dpi=dpi)
        with self.open(pdf_path) as opened:
            return opened.render_page(page_number, dpi, output_dir)

    @staticmethod
    def _safe_close(value: Any) -> None:
        close = getattr(value, "close", None)
        if callable(close):
            close()

    @staticmethod
    def _import_pypdfium2():
        import pypdfium2

        return pypdfium2
