from tests.unit.application.workflows.ingestion._test_ingestion_workflow_support_part1 import *  # noqa: F401,F403

class FailingExtractionWorkflow:
    def __init__(self, message: str = "Malformed extraction response.") -> None:
        self.extraction_model = "extract-test"
        self.extraction_service = None
        self.message = message
        self.calls = []

    def extract(
        self,
        document_id: str,
        chunks,
        activity_context=None,
        progress_callback=None,
        replace_existing: bool = False,
        tables=None,
        sections=None,
        base_result=None,
    ):
        self.calls.append(
            {
                "document_id": document_id,
                "chunks": list(chunks),
                "replace_existing": replace_existing,
                "tables": tables,
                "base_result": base_result,
            }
        )
        from src.shared.exceptions import SchemaValidationError

        raise SchemaValidationError(self.message)

class FakeEmbeddingWorkflow:
    def __init__(self) -> None:
        self.embedding_service = type(
            "EmbeddingService",
            (),
            {"model_name": "embed-test"},
        )()
        self.embed_calls = []
        self.store_calls = []
        self.delete_calls = []

    def embed_chunks(self, chunks, activity_context=None, progress_callback=None):
        self.embed_calls.append(list(chunks))
        embedded = []
        for chunk in chunks:
            embedded.append(
                EmbeddedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    section_id=chunk.section_id,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type,
                    section_path=list(chunk.section_path),
                    element_ids=list(chunk.element_ids),
                    table_ids=list(chunk.table_ids),
                    picture_ids=list(chunk.picture_ids),
                    source=chunk.source,
                    sequence_number=chunk.sequence_number,
                    chunk_index=chunk.chunk_index,
                    chunk_total=chunk.chunk_total,
                    embedding_text=chunk.embedding_text,
                    statistics=chunk.statistics,
                    audit=chunk.audit,
                    embedding=[0.1, 0.2, 0.3],
                )
            )
        return embedded

    def store_embedded_chunks(self, embedded_chunks, progress_callback=None):
        self.store_calls.append(list(embedded_chunks))

    def delete_document_vectors(self, document_id: str) -> None:
        self.delete_calls.append(document_id)

class FakeSemanticLinkingWorkflow:
    def __init__(self, relationships=None) -> None:
        self.relationships = relationships if relationships is not None else []
        self.calls = []

    def link(self, document_id: str):
        self.calls.append(document_id)
        return list(self.relationships)

class FakeDocumentLookupService:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.calls = []

    def get_document_graph(self, document_id: str, activity_context=None):
        self.calls.append(document_id)
        return copy.deepcopy(self.graph) if self.graph is not None else None

class FakeEventService:
    def __init__(self) -> None:
        self.events = []

    def publish(self, event, *, context=None, severity=None):
        self.events.append(event)
        return event

def _build_workflow(
    *,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
    duplicate_service: FakeDuplicateDetectionService | None = None,
    parsing_workflow=None,
    event_service=None,
    extraction_workflow=None,
    document_registration_service=None,
    embedding_workflow=None,
    document_lookup_service=None,
    semantic_linking_workflow=None,
    post_classification_chunk_finalization_workflow=None,
    extraction_enabled: bool = True,
    runtime_capabilities=None,
):
    return IngestionWorkflow(
        unit_of_work=FakeUnitOfWork(),
        ingestion_request_validator=IngestionRequestValidator(),
        duplicate_detection_service=duplicate_service or FakeDuplicateDetectionService(),
        parsing_workflow=parsing_workflow or FakeParsingWorkflow(sample_document_graph),
        document_registration_service=(
            document_registration_service or FakeDocumentRegistrationService()
        ),
        document_classification_workflow=FakeDocumentClassificationWorkflow(
            sample_document_classification
        ),
        post_classification_chunk_finalization_workflow=(
            post_classification_chunk_finalization_workflow
            or FakePostClassificationChunkFinalizationWorkflow(sample_document_graph)
        ),
        extraction_workflow=(
            extraction_workflow
            or FakeExtractionWorkflow(sample_extraction_result)
        ),
        embedding_workflow=embedding_workflow or FakeEmbeddingWorkflow(),
        id_generator=IdGenerator(),
        runtime_capabilities=runtime_capabilities,
        extraction_enabled=extraction_enabled,
        event_service=event_service,
        document_lookup_service=document_lookup_service,
        semantic_linking_workflow=semantic_linking_workflow,
    )

__all__ = [name for name in globals() if not name.startswith("__")]
