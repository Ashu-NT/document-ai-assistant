from __future__ import annotations

from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing import ParsingWorkflow
from src.application.workflows.parsing.builders import (
    DocumentGraphBuilder,
    SectionBuilder,
)
from src.application.workflows.parsing.normalizers import DoclingDocumentNormalizer
from src.application.workflows.parsing.ocr import build_parsing_ocr_runtime
from src.infrastructure.parsing.docling import DoclingParser
from src.shared.ids import IdGenerator


def build_parsing_runtime(
    *,
    id_generator: IdGenerator,
) -> tuple[ParsingWorkflow, DocumentGraphBuilder]:
    """Build the parsing workflow and its document graph builder.

    Shared by every ingestion entrypoint so Docling/OCR/graph-build wiring
    lives in exactly one place.
    """
    ocr_runtime = build_parsing_ocr_runtime(id_generator=id_generator)
    section_builder = SectionBuilder(id_generator)
    document_graph_builder = DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=section_builder,
    )
    parsing_workflow = ParsingWorkflow(
        parser=DoclingParser(),
        normalizer=DoclingDocumentNormalizer(),
        document_graph_builder=document_graph_builder,
        id_generator=id_generator,
        document_graph_validator=DocumentGraphValidator(),
        ocr_policy=ocr_runtime.policy,
        canonical_element_ocr_enricher=ocr_runtime.canonical_element_ocr_enricher,
        page_ocr_fallback_workflow=ocr_runtime.page_ocr_fallback_workflow,
    )
    return parsing_workflow, document_graph_builder
