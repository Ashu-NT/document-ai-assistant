from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing.builders.document_graph_builder import (
    DocumentGraphBuilder,
)
from src.application.workflows.parsing.normalizers.docling_document_normalizer import (
    DoclingDocumentNormalizer,
)
from src.application.workflows.parsing.parsing_workflow_result import (
    ParsingWorkflowResult,
)
from src.domain.document import DocumentGraph, DocumentHashes
from src.infrastructure.parsing.docling.docling_parser import DoclingParser
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix


class ParsingWorkflow:
    def __init__(
        self,
        parser: DoclingParser,
        normalizer: DoclingDocumentNormalizer,
        document_graph_builder: DocumentGraphBuilder,
        id_generator: IdGenerator,
        document_graph_validator: DocumentGraphValidator | None = None,
    ) -> None:
        self.parser = parser
        self.normalizer = normalizer
        self.document_graph_builder = document_graph_builder
        self.id_generator = id_generator
        self.document_graph_validator = document_graph_validator

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

        return self._build_result(
            document_graph=document_graph,
            file_path=file_path,
            page_count=raw_parsed_document.page_count,
        )

    @staticmethod
    def _build_result(
        *,
        document_graph: DocumentGraph,
        file_path: str,
        page_count: int | None,
    ) -> ParsingWorkflowResult:
        return ParsingWorkflowResult(
            document_id=document_graph.document.document_id,
            file_path=file_path,
            page_count=page_count,
            element_count=len(document_graph.elements),
            section_count=len(document_graph.sections),
            chunk_count=len(document_graph.chunks),
            table_count=len(document_graph.tables),
            picture_count=len(document_graph.pictures),
            document_graph=document_graph,
        )
