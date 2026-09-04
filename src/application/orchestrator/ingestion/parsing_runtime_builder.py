from __future__ import annotations

from src.application.orchestrator.ingestion.ingestion_input_limits import (
    resolve_ingestion_input_limits,
)
from src.application.orchestrator.ingestion.parsing_chunking_settings import (
    resolve_parsing_chunking_settings,
)
from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing import ParsingWorkflow
from src.application.workflows.parsing.builders import (
    DocumentGraphBuilder,
    SectionBuilder,
)
from src.application.workflows.parsing.builders.document_graph.cross_references import (
    CrossReferencePipeline,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_linker import (
    ChunkCrossReferenceLinker,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.pdf_link_cross_reference_linker import (
    PdfLinkCrossReferenceLinker,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.reconciliation import (
    CrossReferenceReconciliationService,
)
from src.application.workflows.parsing.normalizers import DoclingDocumentNormalizer
from src.application.workflows.parsing.ocr import build_parsing_ocr_runtime
from src.config.settings import chunking_settings
from src.infrastructure.parsing.docling import DoclingParser
from src.infrastructure.pdf.pdf_link_annotation_extractor import (
    PdfLinkAnnotationExtractor,
)
from src.shared.ids import IdGenerator


def build_parsing_runtime(
    *,
    id_generator: IdGenerator,
) -> tuple[ParsingWorkflow, DocumentGraphBuilder]:
    """Build the parsing workflow and its document graph builder.

    Shared by every ingestion entrypoint so Docling/OCR/graph-build wiring
    lives in exactly one place.
    """
    ingestion_input_limits = resolve_ingestion_input_limits()
    parsing_chunking_settings = resolve_parsing_chunking_settings()
    ocr_runtime = build_parsing_ocr_runtime(id_generator=id_generator)
    section_builder = SectionBuilder(id_generator)
    chunk_cross_reference_linker = (
        ChunkCrossReferenceLinker(id_generator=id_generator)
        if chunking_settings.chunk_cross_reference_detection_enabled
        else None
    )
    pdf_link_cross_reference_linker = (
        PdfLinkCrossReferenceLinker(id_generator=id_generator)
        if chunking_settings.pdf_link_cross_reference_enabled
        else None
    )
    cross_reference_pipeline = None
    if chunk_cross_reference_linker is not None or pdf_link_cross_reference_linker is not None:
        cross_reference_pipeline = CrossReferencePipeline(
            fuzzy_linker=chunk_cross_reference_linker,
            native_linker=pdf_link_cross_reference_linker,
            reconciliation_service=CrossReferenceReconciliationService(
                id_generator=id_generator
            ),
        )
    document_graph_builder = DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=section_builder,
        max_chunk_tokens=parsing_chunking_settings.max_chunk_tokens,
        chunk_overlap=parsing_chunking_settings.chunk_overlap,
        min_section_text_length=parsing_chunking_settings.min_section_text_length,
        cross_reference_pipeline=cross_reference_pipeline,
    )
    pdf_link_annotation_extractor = (
        PdfLinkAnnotationExtractor()
        if chunking_settings.pdf_link_cross_reference_enabled
        else None
    )
    parsing_workflow = ParsingWorkflow(
        parser=DoclingParser(
            max_num_pages=ingestion_input_limits.max_pdf_pages,
            max_file_size_bytes=ingestion_input_limits.max_file_size_bytes,
            timeout_seconds=ingestion_input_limits.parse_timeout_seconds,
        ),
        normalizer=DoclingDocumentNormalizer(),
        document_graph_builder=document_graph_builder,
        id_generator=id_generator,
        document_graph_validator=DocumentGraphValidator(),
        ocr_policy=ocr_runtime.policy,
        canonical_element_ocr_enricher=ocr_runtime.canonical_element_ocr_enricher,
        page_ocr_fallback_workflow=ocr_runtime.page_ocr_fallback_workflow,
        pdf_link_annotation_extractor=pdf_link_annotation_extractor,
    )
    return parsing_workflow, document_graph_builder
