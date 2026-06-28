from pathlib import Path
from typing import Any

from src.infrastructure.pdf.rendered_page import RenderedPage
from src.shared.exceptions import InfrastructureError


class PDFPageRenderer:
    def render_page(
        self,
        pdf_path: str,
        page_number: int,
        dpi: int,
        output_dir: str | Path,
    ) -> RenderedPage:
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

        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = output_directory / f"{Path(pdf_path).stem}_page_{page_number}.png"

        document = None
        page = None
        try:
            pdfium = self._import_pypdfium2()
            document = pdfium.PdfDocument(pdf_path)
            page_index = page_number - 1
            if page_index >= len(document):
                raise InfrastructureError(
                    "Requested page number exceeds the PDF page count.",
                    details={
                        "pdf_path": pdf_path,
                        "page_number": page_number,
                        "page_count": len(document),
                    },
                )

            page = document[page_index]
            bitmap = page.render(scale=dpi / 72.0)
            image = bitmap.to_pil()
            image.save(output_path)
            width, height = image.size
            return RenderedPage(
                pdf_path=pdf_path,
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
                    "pdf_path": pdf_path,
                    "page_number": page_number,
                    "dpi": dpi,
                },
            ) from exc
        finally:
            self._safe_close(page)
            self._safe_close(document)

    @staticmethod
    def _safe_close(value: Any) -> None:
        close = getattr(value, "close", None)
        if callable(close):
            close()

    @staticmethod
    def _import_pypdfium2():
        import pypdfium2

        return pypdfium2

