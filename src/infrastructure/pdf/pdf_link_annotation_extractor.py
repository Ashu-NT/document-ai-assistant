import ctypes

from src.application.contracts.pdf_links import (
    PdfLinkAnnotation,
    PdfLinkExtractionResult,
    PdfLinkPageFailure,
)
from src.domain.common import BoundingBox
from src.infrastructure.pdf.pdfium_process_lock import PDFIUM_PROCESS_LOCK

# pdfium's link-annotation rect is in native PDF page coordinate space
# (origin at the page's bottom-left, y increasing upward) - unlike the
# device/bitmap coordinates PDFPageRenderer works in.
_RECT_COORDINATE_ORIGIN = "pdf_native_bottom_left"


class PdfLinkAnnotationExtractor:
    """Extracts same-document internal PDF link annotations (direct
    destinations and PDFACTION_GOTO actions) directly from a PDF's own
    structure, bypassing Docling entirely (it has no link-annotation
    handling). pypdfium2 has no high-level API for this - raw ctypes calls
    are required (FPDFLink_Enumerate / GetAnnotRect / GetDest / GetAction +
    FPDFAction_GetType / GetDest).

    Satisfies PdfLinkExtractorPort structurally (duck-typed, no explicit
    base class - matching DoclingParser's relationship to ParserPort).
    """

    def extract(self, file_path: str) -> PdfLinkExtractionResult:
        pdfium = self._import_pypdfium2()
        raw = pdfium.raw

        with PDFIUM_PROCESS_LOCK:
            try:
                document = pdfium.PdfDocument(file_path)
            except Exception as exc:
                return PdfLinkExtractionResult(
                    status="failed",
                    error_message=str(exc),
                )

            try:
                try:
                    page_count = len(document)
                except Exception as exc:
                    return PdfLinkExtractionResult(
                        status="failed",
                        error_message=str(exc),
                    )

                annotations: list[PdfLinkAnnotation] = []
                page_failures: list[PdfLinkPageFailure] = []
                non_internal_links_excluded = 0
                invalid_destinations_skipped = 0

                for page_number in range(1, page_count + 1):
                    try:
                        (
                            page_annotations,
                            page_non_internal,
                            page_invalid,
                        ) = self._extract_page_links(
                            document=document,
                            raw=raw,
                            page_number=page_number,
                            page_count=page_count,
                        )
                        annotations.extend(page_annotations)
                        non_internal_links_excluded += page_non_internal
                        invalid_destinations_skipped += page_invalid
                    except Exception as exc:
                        # One bad page must not sink the whole file.
                        page_failures.append(
                            PdfLinkPageFailure(
                                page_number=page_number,
                                error_message=str(exc),
                            )
                        )
                        continue

                return PdfLinkExtractionResult(
                    annotations=annotations,
                    non_internal_links_excluded=non_internal_links_excluded,
                    invalid_destinations_skipped=invalid_destinations_skipped,
                    status="partial" if page_failures else "ok",
                    page_failures=page_failures,
                )
            finally:
                document.close()

    def _extract_page_links(
        self,
        *,
        document,
        raw,
        page_number: int,
        page_count: int,
    ) -> tuple[list[PdfLinkAnnotation], int, int]:
        page = document[page_number - 1]
        try:
            page_raw = page.raw
            doc_raw = document.raw
            width, height = page.get_size()
            rotation_degrees = page.get_rotation()
            source_page_label = document.get_page_label(page_number - 1) or None

            annotations: list[PdfLinkAnnotation] = []
            non_internal_links_excluded = 0
            invalid_destinations_skipped = 0

            start_pos = ctypes.c_long(0)
            while True:
                link_handle = raw.FPDF_LINK()
                enumerated = raw.FPDFLink_Enumerate(
                    page_raw,
                    ctypes.byref(start_pos),
                    ctypes.byref(link_handle),
                )
                if not enumerated:
                    break

                link_kind, dest_handle = self._resolve_link_kind(
                    raw=raw,
                    doc_raw=doc_raw,
                    link_handle=link_handle,
                )
                if link_kind is None:
                    non_internal_links_excluded += 1
                    continue

                dest_index = raw.FPDFDest_GetDestPageIndex(doc_raw, dest_handle)
                if dest_index is None or not (0 <= dest_index < page_count):
                    invalid_destinations_skipped += 1
                    continue

                annotations.append(
                    PdfLinkAnnotation(
                        source_page=page_number,
                        dest_page=dest_index + 1,
                        link_kind=link_kind,
                        source_rect=self._resolve_source_rect(
                            raw=raw, link_handle=link_handle
                        ),
                        rect_coordinate_origin=_RECT_COORDINATE_ORIGIN,
                        source_page_size=(width, height),
                        source_page_rotation_degrees=rotation_degrees,
                        source_page_label=source_page_label,
                        dest_page_label=(
                            document.get_page_label(dest_index) or None
                        ),
                    )
                )

            return annotations, non_internal_links_excluded, invalid_destinations_skipped
        finally:
            page.close()

    @staticmethod
    def _resolve_link_kind(*, raw, doc_raw, link_handle):
        """Try a direct destination first; only follow a GOTO action.
        Anything else (unsupported/remote-goto/URI/launch/embedded-goto, or
        no dest and no GOTO action) is not same-document-internal."""
        dest_handle = raw.FPDFLink_GetDest(doc_raw, link_handle)
        if dest_handle:
            return "direct_destination", dest_handle

        action_handle = raw.FPDFLink_GetAction(link_handle)
        if not action_handle:
            return None, None

        if raw.FPDFAction_GetType(action_handle) != raw.PDFACTION_GOTO:
            return None, None

        dest_handle = raw.FPDFAction_GetDest(doc_raw, action_handle)
        if not dest_handle:
            return None, None

        return "goto", dest_handle

    @staticmethod
    def _resolve_source_rect(*, raw, link_handle) -> BoundingBox:
        rect = raw.FS_RECTF()
        if not raw.FPDFLink_GetAnnotRect(link_handle, ctypes.byref(rect)):
            return BoundingBox(x1=0.0, y1=0.0, x2=0.0, y2=0.0)
        return BoundingBox(
            x1=rect.left,
            y1=rect.bottom,
            x2=rect.right,
            y2=rect.top,
        )

    @staticmethod
    def _import_pypdfium2():
        import pypdfium2

        return pypdfium2


__all__ = ["PdfLinkAnnotationExtractor"]
