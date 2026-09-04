from typing import Protocol

from src.application.contracts.pdf_links.pdf_link_extraction_result import (
    PdfLinkExtractionResult,
)


class PdfLinkExtractorPort(Protocol):
    def extract(self, file_path: str) -> PdfLinkExtractionResult:
        ...


__all__ = ["PdfLinkExtractorPort"]
