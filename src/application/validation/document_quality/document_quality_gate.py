from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.validation.document_quality.chunking_quality_checks import (
    check_chunks_have_section_paths,
    check_general_chunk_ratio,
    check_maintenance_headings_have_chunks,
)
from src.application.validation.document_quality.document_quality_result import (
    DocumentQualityResult,
)
from src.application.validation.document_quality.ocr_quality_checks import (
    check_ocr_target_failures,
    check_ocr_targets_have_page_numbers,
)
from src.application.validation.document_quality.parser_quality_checks import (
    check_elements_have_pages,
    check_orphan_element_ratio,
    check_section_count,
)
from src.application.validation.document_quality.retrieval_quality_checks import (
    check_retrieved_chunk_scores,
    check_retrieved_chunks_have_content,
)

if TYPE_CHECKING:
    from src.domain.document import DocumentChunk, DocumentSection
    from src.domain.elements import CanonicalElement
    from src.domain.retrieval import RetrievedChunk


class DocumentQualityGate:
    """Runs a suite of quality checks across parsing, chunking, and retrieval outputs."""

    def check_parsing(
        self,
        document_id: str,
        *,
        sections: list[DocumentSection],
        elements: list[CanonicalElement],
        ocr_trace=None,
    ) -> DocumentQualityResult:
        result = DocumentQualityResult(document_id=document_id)
        result.checks.append(check_section_count(sections))
        result.checks.append(check_orphan_element_ratio(elements, sections))
        result.checks.append(check_elements_have_pages(elements))
        result.checks.append(check_ocr_target_failures(ocr_trace))
        result.checks.append(check_ocr_targets_have_page_numbers(ocr_trace))
        return result

    def check_chunking(
        self,
        document_id: str,
        *,
        chunks: list[DocumentChunk],
    ) -> DocumentQualityResult:
        result = DocumentQualityResult(document_id=document_id)
        result.checks.append(check_general_chunk_ratio(chunks))
        result.checks.append(check_chunks_have_section_paths(chunks))
        result.checks.append(check_maintenance_headings_have_chunks(chunks))
        return result

    def check_retrieval(
        self,
        document_id: str,
        *,
        chunks: list[RetrievedChunk],
    ) -> DocumentQualityResult:
        result = DocumentQualityResult(document_id=document_id)
        result.checks.append(check_retrieved_chunk_scores(chunks))
        result.checks.append(check_retrieved_chunks_have_content(chunks))
        return result
