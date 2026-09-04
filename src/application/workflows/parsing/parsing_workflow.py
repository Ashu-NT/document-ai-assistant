import time
from collections.abc import Callable
from pathlib import Path

from src.application.contracts.parsing import ParserPort
from src.application.contracts.pdf_links import PdfLinkExtractorPort
from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing.canonical_element_ocr_enricher import (
    CanonicalElementOCREnricher,
)
from src.application.workflows.parsing.builders.document_graph_builder import (
    DocumentGraphBuilder,
)
from src.application.workflows.parsing.ocr.parsing_ocr_policy import (
    ParsingOCRPolicy,
    resolve_parsing_ocr_policy,
)
from src.application.workflows.parsing.ocr import PageOCRFallbackWorkflow
from src.application.workflows.parsing.normalizers.docling_document_normalizer import (
    DoclingDocumentNormalizer,
)
from src.application.workflows.parsing.parsing_workflow_result import (
    ParsingWorkflowResult,
)
from src.application.workflows.parsing.parsing_workflow_result_builder import (
    build_parsing_workflow_result,
)
from src.application.workflows.parsing.runtime.parsing_stage_runner import run_stage
from src.config.logging import get_logger
from src.domain.document import DocumentGraph, DocumentHashes
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.formatting.duration_formatter import format_elapsed_seconds
from src.shared.ids import IdGenerator, IdPrefix
from src.shared.progress.progress_emitter import emit_progress

_logger = get_logger(__name__)


class ParsingWorkflow:
    def __init__(
        self,
        parser: ParserPort,
        normalizer: DoclingDocumentNormalizer,
        document_graph_builder: DocumentGraphBuilder,
        id_generator: IdGenerator,
        document_graph_validator: DocumentGraphValidator | None = None,
        ocr_policy: ParsingOCRPolicy | None = None,
        canonical_element_ocr_enricher: CanonicalElementOCREnricher | None = None,
        page_ocr_fallback_workflow: PageOCRFallbackWorkflow | None = None,
        pdf_link_annotation_extractor: PdfLinkExtractorPort | None = None,
        audit_service=None,
    ) -> None:
        self.parser = parser
        self.normalizer = normalizer
        self.document_graph_builder = document_graph_builder
        self.id_generator = id_generator
        self.document_graph_validator = document_graph_validator
        self.ocr_policy = ocr_policy
        self.canonical_element_ocr_enricher = canonical_element_ocr_enricher
        self.page_ocr_fallback_workflow = page_ocr_fallback_workflow
        self.pdf_link_annotation_extractor = pdf_link_annotation_extractor
        self.audit_service = audit_service
        self.last_pdf_link_extraction_result = None

    @tracked_action(
        action="parsing.workflow_completed",
        entity_type="document",
        activity=True,
        audit=True,
        event=False,
    )
    def parse(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        document_id: str | None = None,
        enable_ocr_override: bool | None = None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> ParsingWorkflowResult:
        resolved_document_id = document_id or self.id_generator.new_id(IdPrefix.DOCUMENT)
        file_name = Path(file_path).name or file_path
        total_started_at = time.perf_counter()
        stage_durations: dict[str, float] = {}
        resolved_ocr_policy = self._resolve_ocr_policy(enable_ocr_override)

        emit_progress(
            progress_callback,
            f"Parsing workflow started for {file_name}.",
        )
        raw_parsed_document = run_stage(
            progress_callback=progress_callback,
            start_message=(
                f"Docling conversion started for {file_name}. "
                "This can take a while for large or image-heavy PDFs."
            ),
            heartbeat_label=f"Docling conversion for {file_name}",
            failure_label=f"Docling conversion for {file_name}",
            operation=lambda: self.parser.parse(
                file_path,
                enable_ocr_override=enable_ocr_override,
            ),
            completion_message_builder=lambda result, elapsed_seconds: (
                "Docling conversion completed in "
                f"{format_elapsed_seconds(elapsed_seconds)} "
                f"(pages={result.page_count or 'unknown'}, "
                f"parser={result.parser_name})."
            ),
            stage_name="docling_conversion",
            stage_durations=stage_durations,
            document_id=resolved_document_id,
        )
        normalization_item_errors: list[str] = []
        canonical_elements = run_stage(
            progress_callback=progress_callback,
            start_message="Normalizing Docling output into canonical elements...",
            heartbeat_label="Canonical normalization",
            failure_label="Canonical normalization",
            operation=lambda: self.normalizer.normalize(
                raw_parsed_document,
                resolved_document_id,
                skipped_item_errors=normalization_item_errors,
            ),
            completion_message_builder=lambda result, elapsed_seconds: (
                "Canonical normalization completed in "
                f"{format_elapsed_seconds(elapsed_seconds)} "
                f"({len(result)} canonical element(s))."
            ),
            stage_name="canonical_normalization",
            stage_durations=stage_durations,
            document_id=resolved_document_id,
        )
        ocr_trace = None
        if (
            self.canonical_element_ocr_enricher is not None
            and resolved_ocr_policy.canonical_enrichment_enabled
        ):
            canonical_elements = run_stage(
                progress_callback=progress_callback,
                start_message=(
                    "Running canonical element OCR enrichment for "
                    f"{len(canonical_elements)} element(s)..."
                ),
                heartbeat_label="Canonical element OCR enrichment",
                failure_label="Canonical element OCR enrichment",
                operation=lambda: self.canonical_element_ocr_enricher.enrich(
                    canonical_elements,
                    activity_context=activity_context,
                ),
                completion_message_builder=lambda result, elapsed_seconds: (
                    "Canonical element OCR enrichment completed in "
                    f"{format_elapsed_seconds(elapsed_seconds)} "
                    f"({len(result)} element(s))."
                ),
                stage_name="canonical_element_ocr_enrichment",
                stage_durations=stage_durations,
                document_id=resolved_document_id,
            )
        if (
            self.page_ocr_fallback_workflow is not None
            and resolved_ocr_policy.page_fallback_runtime_enabled
        ):
            ocr_merge_result = run_stage(
                progress_callback=progress_callback,
                start_message=(
                    "Running page OCR fallback across "
                    f"{raw_parsed_document.page_count or 'unknown'} page(s)..."
                ),
                heartbeat_label="Page OCR fallback",
                failure_label="Page OCR fallback",
                operation=lambda: self.page_ocr_fallback_workflow.run(
                    file_path=file_path,
                    canonical_elements=canonical_elements,
                    page_count=raw_parsed_document.page_count,
                    activity_context=activity_context,
                ),
                completion_message_builder=lambda result, elapsed_seconds: (
                    "Page OCR fallback completed in "
                    f"{format_elapsed_seconds(elapsed_seconds)} "
                    f"({len(result.canonical_elements)} element(s))."
                ),
                stage_name="page_ocr_fallback",
                stage_durations=stage_durations,
                document_id=resolved_document_id,
            )
            canonical_elements = ocr_merge_result.canonical_elements
            ocr_trace = ocr_merge_result.ocr_trace

        pdf_link_extraction_result = None
        if self.pdf_link_annotation_extractor is not None:
            pdf_link_extraction_result = run_stage(
                progress_callback=progress_callback,
                start_message=f"Extracting PDF link annotations for {file_name}...",
                heartbeat_label=f"PDF link extraction for {file_name}",
                failure_label=f"PDF link extraction for {file_name}",
                operation=lambda: self.pdf_link_annotation_extractor.extract(
                    file_path
                ),
                completion_message_builder=lambda result, elapsed_seconds: (
                    "PDF link extraction completed in "
                    f"{format_elapsed_seconds(elapsed_seconds)} "
                    f"({len(result.annotations)} annotation(s), "
                    f"status={result.status})."
                ),
                stage_name="pdf_link_extraction",
                stage_durations=stage_durations,
                document_id=resolved_document_id,
            )
            if pdf_link_extraction_result.status != "ok":
                _logger.warning(
                    "pdf_link_extraction_degraded document_id=%s status=%s "
                    "page_failures=%s non_internal_links_excluded=%s "
                    "invalid_destinations_skipped=%s error=%r",
                    resolved_document_id,
                    pdf_link_extraction_result.status,
                    len(pdf_link_extraction_result.page_failures),
                    pdf_link_extraction_result.non_internal_links_excluded,
                    pdf_link_extraction_result.invalid_destinations_skipped,
                    pdf_link_extraction_result.error_message,
                )
        self.last_pdf_link_extraction_result = pdf_link_extraction_result

        graph_build_element_errors: list[str] = []
        document_graph = run_stage(
            progress_callback=progress_callback,
            start_message=(
                "Building document graph from "
                f"{len(canonical_elements)} canonical element(s)..."
            ),
            heartbeat_label="Document graph build",
            failure_label="Document graph build",
            operation=lambda: self.document_graph_builder.build(
                document_id=resolved_document_id,
                file_path=file_path,
                hashes=DocumentHashes(
                    file_hash=file_hash,
                    content_hash=content_hash,
                ),
                canonical_elements=canonical_elements,
                raw_parsed_document=raw_parsed_document,
                skipped_element_errors=graph_build_element_errors,
                pdf_link_extraction_result=pdf_link_extraction_result,
            ),
            completion_message_builder=lambda result, elapsed_seconds: (
                "Document graph build completed in "
                f"{format_elapsed_seconds(elapsed_seconds)} "
                f"(sections={len(result.sections)}, "
                f"elements={len(result.elements)}, "
                f"chunks={len(result.chunks)})."
            ),
            stage_name="graph_build",
            stage_durations=stage_durations,
            document_id=resolved_document_id,
        )

        if self.document_graph_validator is not None:
            run_stage(
                progress_callback=progress_callback,
                start_message="Validating document graph...",
                heartbeat_label="Document graph validation",
                failure_label="Document graph validation",
                operation=lambda: self._validate_document_graph(document_graph),
                completion_message_builder=lambda _result, elapsed_seconds: (
                    "Document graph validation completed in "
                    f"{format_elapsed_seconds(elapsed_seconds)}."
                ),
                stage_name="graph_validation",
                stage_durations=stage_durations,
                document_id=resolved_document_id,
            )

        total_elapsed_seconds = time.perf_counter() - total_started_at
        stage_durations["total"] = total_elapsed_seconds

        result = build_parsing_workflow_result(
            document_graph=document_graph,
            file_path=file_path,
            page_count=raw_parsed_document.page_count,
            ocr_trace=ocr_trace,
            stage_durations=stage_durations,
            normalization_item_errors=normalization_item_errors,
            graph_build_item_errors=graph_build_element_errors,
        )

        emit_progress(
            progress_callback,
            "Parsing workflow completed in "
            f"{format_elapsed_seconds(total_elapsed_seconds)} "
            f"(pages={raw_parsed_document.page_count or 'unknown'}, "
            f"canonical_elements={len(canonical_elements)}, "
            f"sections={len(document_graph.sections)}, "
            f"chunks={len(document_graph.chunks)}).",
        )
        return result

    def _validate_document_graph(self, document_graph: DocumentGraph) -> None:
        validation = self.document_graph_validator.validate(document_graph)
        validation.raise_if_invalid()

    def _resolve_ocr_policy(
        self,
        enable_ocr_override: bool | None,
    ) -> ParsingOCRPolicy:
        if self.ocr_policy is None:
            return resolve_parsing_ocr_policy(
                enable_docling_ocr_override=enable_ocr_override
            )
        return self.ocr_policy.with_docling_ocr_override(enable_ocr_override)
