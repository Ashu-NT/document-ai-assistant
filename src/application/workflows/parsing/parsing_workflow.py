import time
from collections.abc import Callable
from pathlib import Path
from threading import Event, Thread
from typing import TypeVar

from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing.canonical_element_ocr_enricher import (
    CanonicalElementOCREnricher,
)
from src.application.workflows.parsing.builders.document_graph_builder import (
    DocumentGraphBuilder,
)
from src.application.workflows.parsing.ocr import PageOCRFallbackWorkflow
from src.application.workflows.parsing.normalizers.docling_document_normalizer import (
    DoclingDocumentNormalizer,
)
from src.application.workflows.parsing.parsing_workflow_result import (
    ParsingWorkflowResult,
)
from src.application.workflows.parsing.reports import (
    ChunkingReportWriter,
    ParsingReportWriter,
    QualityReportWriter,
)
from src.domain.document import DocumentGraph, DocumentHashes
from src.infrastructure.parsing.docling.docling_parser import DoclingParser
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix

_STAGE_HEARTBEAT_INTERVAL_SECONDS = 30.0
T = TypeVar("T")


def _compute_parse_confidence(
    *,
    element_count: int,
    orphan_count: int,
    no_page_count: int,
) -> float | None:
    if element_count == 0:
        return None
    orphan_ratio = orphan_count / element_count
    no_page_ratio = no_page_count / element_count
    return round(1.0 - (orphan_ratio * 0.5 + no_page_ratio * 0.5), 4)


def _collect_parse_warnings(
    *,
    element_count: int,
    orphan_count: int,
    no_page_count: int,
    section_count: int,
    chunk_count: int,
) -> list[str]:
    warnings: list[str] = []
    if element_count > 0 and orphan_count / element_count > 0.25:
        warnings.append(
            f"High orphan element ratio: {orphan_count}/{element_count} elements have no section"
        )
    if element_count > 0 and no_page_count / element_count > 0.5:
        warnings.append(
            f"Many elements lack page numbers: {no_page_count}/{element_count}"
        )
    if section_count == 0:
        warnings.append("Document produced no sections")
    if chunk_count == 0:
        warnings.append("Document produced no chunks")
    return warnings


def _format_elapsed_seconds(elapsed_seconds: float) -> str:
    if elapsed_seconds < 1:
        return f"{elapsed_seconds:.2f}s"
    if elapsed_seconds < 60:
        return f"{elapsed_seconds:.1f}s"

    minutes, seconds = divmod(elapsed_seconds, 60.0)
    if minutes < 60:
        return f"{int(minutes)}m {seconds:.1f}s"

    hours, minutes = divmod(minutes, 60.0)
    return f"{int(hours)}h {int(minutes)}m {seconds:.1f}s"


class _StageHeartbeat:
    def __init__(
        self,
        *,
        label: str,
        progress_callback: Callable[[str], None] | None,
        interval_seconds: float = _STAGE_HEARTBEAT_INTERVAL_SECONDS,
    ) -> None:
        self.label = label
        self.progress_callback = progress_callback
        self.interval_seconds = interval_seconds
        self._started_at = 0.0
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self.progress_callback is None or self._thread is not None:
            return

        self._started_at = time.perf_counter()
        self._thread = Thread(
            target=self._run,
            name="parsing-stage-heartbeat",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return

        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=0.1)

    def _run(self) -> None:
        while not self._stop_event.wait(self.interval_seconds):
            elapsed_seconds = time.perf_counter() - self._started_at
            self.progress_callback(
                f"{self.label} still running... "
                f"({_format_elapsed_seconds(elapsed_seconds)} elapsed)"
            )


class ParsingWorkflow:
    def __init__(
        self,
        parser: DoclingParser,
        normalizer: DoclingDocumentNormalizer,
        document_graph_builder: DocumentGraphBuilder,
        id_generator: IdGenerator,
        document_graph_validator: DocumentGraphValidator | None = None,
        canonical_element_ocr_enricher: CanonicalElementOCREnricher | None = None,
        page_ocr_fallback_workflow: PageOCRFallbackWorkflow | None = None,
        parsing_report_writer: ParsingReportWriter | None = None,
        chunking_report_writer: ChunkingReportWriter | None = None,
        quality_report_writer: QualityReportWriter | None = None,
    ) -> None:
        self.parser = parser
        self.normalizer = normalizer
        self.document_graph_builder = document_graph_builder
        self.id_generator = id_generator
        self.document_graph_validator = document_graph_validator
        self.canonical_element_ocr_enricher = canonical_element_ocr_enricher
        self.page_ocr_fallback_workflow = page_ocr_fallback_workflow
        self.parsing_report_writer = parsing_report_writer
        self.chunking_report_writer = chunking_report_writer
        self.quality_report_writer = quality_report_writer

    @tracked_action(
        action="parsing.workflow_completed",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def parse(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        document_id: str | None = None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> ParsingWorkflowResult:
        resolved_document_id = document_id or self.id_generator.new_id(IdPrefix.DOCUMENT)
        file_name = Path(file_path).name or file_path
        total_started_at = time.perf_counter()

        self._emit_progress(
            progress_callback,
            f"Parsing workflow started for {file_name}.",
        )
        raw_parsed_document = self._run_stage(
            progress_callback=progress_callback,
            start_message=(
                f"Docling conversion started for {file_name}. "
                "This can take a while for large or image-heavy PDFs."
            ),
            heartbeat_label=f"Docling conversion for {file_name}",
            failure_label=f"Docling conversion for {file_name}",
            operation=lambda: self.parser.parse(file_path),
            completion_message_builder=lambda result, elapsed_seconds: (
                "Docling conversion completed in "
                f"{_format_elapsed_seconds(elapsed_seconds)} "
                f"(pages={result.page_count or 'unknown'}, "
                f"parser={result.parser_name})."
            ),
        )
        canonical_elements = self._run_stage(
            progress_callback=progress_callback,
            start_message="Normalizing Docling output into canonical elements...",
            heartbeat_label="Canonical normalization",
            failure_label="Canonical normalization",
            operation=lambda: self.normalizer.normalize(
                raw_parsed_document,
                resolved_document_id,
            ),
            completion_message_builder=lambda result, elapsed_seconds: (
                "Canonical normalization completed in "
                f"{_format_elapsed_seconds(elapsed_seconds)} "
                f"({len(result)} canonical element(s))."
            ),
        )
        ocr_trace = None
        if self.canonical_element_ocr_enricher is not None:
            canonical_elements = self._run_stage(
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
                    f"{_format_elapsed_seconds(elapsed_seconds)} "
                    f"({len(result)} element(s))."
                ),
            )
        if self.page_ocr_fallback_workflow is not None:
            ocr_merge_result = self._run_stage(
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
                    f"{_format_elapsed_seconds(elapsed_seconds)} "
                    f"({len(result.canonical_elements)} element(s))."
                ),
            )
            canonical_elements = ocr_merge_result.canonical_elements
            ocr_trace = ocr_merge_result.ocr_trace

        document_graph = self._run_stage(
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
            ),
            completion_message_builder=lambda result, elapsed_seconds: (
                "Document graph build completed in "
                f"{_format_elapsed_seconds(elapsed_seconds)} "
                f"(sections={len(result.sections)}, "
                f"elements={len(result.elements)}, "
                f"chunks={len(result.chunks)})."
            ),
        )

        if self.document_graph_validator is not None:
            self._run_stage(
                progress_callback=progress_callback,
                start_message="Validating document graph...",
                heartbeat_label="Document graph validation",
                failure_label="Document graph validation",
                operation=lambda: self._validate_document_graph(document_graph),
                completion_message_builder=lambda _result, elapsed_seconds: (
                    "Document graph validation completed in "
                    f"{_format_elapsed_seconds(elapsed_seconds)}."
                ),
            )

        result = self._build_result(
            document_graph=document_graph,
            file_path=file_path,
            page_count=raw_parsed_document.page_count,
            ocr_trace=ocr_trace,
        )

        if self.parsing_report_writer is not None:
            self.parsing_report_writer.write(result)
        if self.chunking_report_writer is not None:
            self.chunking_report_writer.write(result)
        if self.quality_report_writer is not None:
            self.quality_report_writer.write(result)

        total_elapsed_seconds = time.perf_counter() - total_started_at
        self._emit_progress(
            progress_callback,
            "Parsing workflow completed in "
            f"{_format_elapsed_seconds(total_elapsed_seconds)} "
            f"(pages={raw_parsed_document.page_count or 'unknown'}, "
            f"canonical_elements={len(canonical_elements)}, "
            f"sections={len(document_graph.sections)}, "
            f"chunks={len(document_graph.chunks)}).",
        )
        return result

    def _validate_document_graph(self, document_graph: DocumentGraph) -> None:
        validation = self.document_graph_validator.validate(document_graph)
        validation.raise_if_invalid()

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)

    def _run_stage(
        self,
        *,
        progress_callback: Callable[[str], None] | None,
        start_message: str,
        heartbeat_label: str,
        failure_label: str,
        operation: Callable[[], T],
        completion_message_builder: Callable[[T, float], str],
    ) -> T:
        self._emit_progress(progress_callback, start_message)
        started_at = time.perf_counter()
        heartbeat = _StageHeartbeat(
            label=heartbeat_label,
            progress_callback=progress_callback,
        )
        heartbeat.start()
        try:
            result = operation()
        except Exception:
            elapsed_seconds = time.perf_counter() - started_at
            self._emit_progress(
                progress_callback,
                f"{failure_label} failed after "
                f"{_format_elapsed_seconds(elapsed_seconds)}.",
            )
            raise
        finally:
            heartbeat.stop()

        elapsed_seconds = time.perf_counter() - started_at
        self._emit_progress(
            progress_callback,
            completion_message_builder(result, elapsed_seconds),
        )
        return result

    @staticmethod
    def _build_result(
        *,
        document_graph: DocumentGraph,
        file_path: str,
        page_count: int | None,
        ocr_trace=None,
    ) -> ParsingWorkflowResult:
        elements = list(document_graph.elements.values())
        orphan_count = sum(1 for e in elements if e.parent_section_id is None)
        no_page_count = sum(
            1 for e in elements if e.source.page_start is None
        )
        parse_confidence = _compute_parse_confidence(
            element_count=len(elements),
            orphan_count=orphan_count,
            no_page_count=no_page_count,
        )
        warnings = _collect_parse_warnings(
            element_count=len(elements),
            orphan_count=orphan_count,
            no_page_count=no_page_count,
            section_count=len(document_graph.sections),
            chunk_count=len(document_graph.chunks),
        )
        if ocr_trace is not None:
            warnings.extend(
                warning
                for warning in ocr_trace.warnings
                if warning not in warnings
            )
        return ParsingWorkflowResult(
            document_id=document_graph.document.document_id,
            file_path=file_path,
            page_count=page_count,
            element_count=len(elements),
            section_count=len(document_graph.sections),
            chunk_count=len(document_graph.chunks),
            table_count=len(document_graph.tables),
            picture_count=len(document_graph.pictures),
            document_graph=document_graph,
            parse_confidence=parse_confidence,
            orphan_element_count=orphan_count,
            elements_without_page_count=no_page_count,
            parse_warnings=warnings,
            ocr_trace=ocr_trace,
        )
