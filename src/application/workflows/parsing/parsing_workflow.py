from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing.canonical_element_ocr_enricher import (
    CanonicalElementOCREnricher,
)
from src.application.workflows.parsing.builders.document_graph_builder import (
    DocumentGraphBuilder,
)
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


class ParsingWorkflow:
    def __init__(
        self,
        parser: DoclingParser,
        normalizer: DoclingDocumentNormalizer,
        document_graph_builder: DocumentGraphBuilder,
        id_generator: IdGenerator,
        document_graph_validator: DocumentGraphValidator | None = None,
        canonical_element_ocr_enricher: CanonicalElementOCREnricher | None = None,
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
    ) -> ParsingWorkflowResult:
        resolved_document_id = document_id or self.id_generator.new_id(IdPrefix.DOCUMENT)

        raw_parsed_document = self.parser.parse(file_path)
        canonical_elements = self.normalizer.normalize(
            raw_parsed_document,
            resolved_document_id,
        )
        if self.canonical_element_ocr_enricher is not None:
            canonical_elements = self.canonical_element_ocr_enricher.enrich(
                canonical_elements,
                activity_context=activity_context,
            )

        document_graph = self.document_graph_builder.build(
            document_id=resolved_document_id,
            file_path=file_path,
            hashes=DocumentHashes(
                file_hash=file_hash,
                content_hash=content_hash,
            ),
            canonical_elements=canonical_elements,
            raw_parsed_document=raw_parsed_document,
        )

        if self.document_graph_validator is not None:
            validation = self.document_graph_validator.validate(document_graph)
            validation.raise_if_invalid()

        result = self._build_result(
            document_graph=document_graph,
            file_path=file_path,
            page_count=raw_parsed_document.page_count,
        )

        if self.parsing_report_writer is not None:
            self.parsing_report_writer.write(result)
        if self.chunking_report_writer is not None:
            self.chunking_report_writer.write(result)
        if self.quality_report_writer is not None:
            self.quality_report_writer.write(result)

        return result

    @staticmethod
    def _build_result(
        *,
        document_graph: DocumentGraph,
        file_path: str,
        page_count: int | None,
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
        )
