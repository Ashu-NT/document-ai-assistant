from dataclasses import dataclass, field
from typing import Literal

from src.application.contracts.pdf_links.pdf_link_annotation import PdfLinkAnnotation


@dataclass(slots=True, frozen=True)
class PdfLinkPageFailure:
    page_number: int
    error_message: str


@dataclass(slots=True, frozen=True)
class PdfLinkExtractionResult:
    annotations: list[PdfLinkAnnotation] = field(default_factory=list)
    # Links whose action type is not a same-document GOTO (unsupported,
    # remote-goto, URI, launch, embedded-goto). Named for what they aren't
    # (same-document-internal), not "external" in the everyday sense.
    non_internal_links_excluded: int = 0
    invalid_destinations_skipped: int = 0
    status: Literal["ok", "partial", "failed"] = "ok"
    page_failures: list[PdfLinkPageFailure] = field(default_factory=list)
    # Set only when status == "failed" (the whole file couldn't be opened).
    error_message: str | None = None


__all__ = ["PdfLinkExtractionResult", "PdfLinkPageFailure"]
