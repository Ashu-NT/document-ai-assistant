from src.application.contracts.document import DocumentRepository
from src.application.validation.document import DocumentGraphValidator
from src.domain.document import DocumentGraph
from src.shared.activity import ActivityContext
from src.shared.execution import ActionResult, tracked_action


class DocumentRegistrationService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        document_graph_validator: DocumentGraphValidator,
    ) -> None:
        self.document_repository = document_repository
        self.document_graph_validator = document_graph_validator

    @tracked_action(
        action="document.registered",
        entity_type="document",
        activity=True,
        audit=True,
        event=True,
    )
    def register_document_graph(
        self,
        document_graph: DocumentGraph,
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        validation = self.document_graph_validator.validate(document_graph)
        validation.raise_if_invalid()

        self.document_repository.save_document_graph(document_graph)

        document_id = document_graph.document.document_id

        return ActionResult(
            entity_type="document",
            entity_id=document_id,
            message="Document graph registered.",
            payload={
                "document_id": document_id,
                "file_name": document_graph.document.file_name,
                "section_count": len(document_graph.sections),
                "element_count": len(document_graph.elements),
                "chunk_count": len(document_graph.chunks),
                "identifier_count": len(document_graph.identifiers),
            },
        )
