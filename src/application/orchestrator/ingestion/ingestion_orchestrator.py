from __future__ import annotations

from src.application.contracts import UnitOfWork
from src.application.orchestrator.ingestion.ingestion_input_limits import (
    resolve_ingestion_input_limits,
)
from src.application.orchestrator.ingestion.ingestion_runtime import IngestionRuntime
from src.application.orchestrator.ingestion.parsing_runtime_builder import (
    build_parsing_runtime,
)
from src.application.orchestrator.ingestion.vector_runtime_builder import (
    build_embedding_workflow,
    build_vector_store,
)
from src.application.services.ai import LLMService
from src.application.services.classification import ClassificationService
from src.application.services.document import (
    DeterministicIdentifierScanner,
    DocumentLookupService,
    DocumentRegistrationService,
    DuplicateDetectionService,
    IdentifierPromotionService,
)
from src.application.services.extraction import ExtractionService
from src.application.services.question_generation import QuestionGenerationService
from src.application.validation.classification import DocumentClassificationValidator
from src.application.validation.document import DocumentGraphValidator
from src.application.validation.extraction import ExtractionResultValidator
from src.application.validation.ingestion import IngestionRequestValidator
from src.application.workflows.classification import (
    ChunkTypeClassificationWorkflow,
    DocumentClassificationWorkflow,
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.ingestion import DeleteDocumentWorkflow, IngestionWorkflow
from src.application.workflows.ingestion.runtime import (
    IngestionRuntimeProfileResolver,
)
from src.application.workflows.linking import SemanticLinkingWorkflow
from src.bootstrap.startup import bootstrap_application
from src.config.settings import (
    classification_settings,
    embedding_settings,
    extraction_settings,
    ingestion_settings,
    llm_settings,
    qdrant_settings,
)
from src.infrastructure.ai.embeddings import create_embedding_provider
from src.infrastructure.ai.llm import OllamaLLMProvider
from src.infrastructure.db.schema_management import ensure_database_schema
from src.infrastructure.db.session import SessionLocal, engine
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from src.shared.ids import IdGenerator


def build_ingestion_runtime(
    *,
    unit_of_work: UnitOfWork | None = None,
    id_generator: IdGenerator | None = None,
    bootstrap: bool = True,
    vector_store=None,
    qdrant_client=None,
    embedding_provider=None,
) -> IngestionRuntime:
    """Build the canonical, fully-wired ingestion dependency graph.

    This is the single composition root for `IngestionWorkflow` and the
    services that commonly run alongside it. Every entrypoint that needs to
    run ingestion (benchmark corpus seeding today; a production ingest
    CLI/tool in the future) should call this instead of re-assembling the
    dependency graph inline, so wiring changes only need to happen once.

    `vector_store`/`qdrant_client`/`embedding_provider` are optional escape
    hatches for callers that already have a live Qdrant client open (e.g. the
    interactive agent runtime): passing them in reuses that client instead of
    opening a second one, which matters in `QDRANT_MODE=local` where a second
    embedded client pointed at the same storage path would fail to open.
    """
    if bootstrap:
        bootstrap_application()
        ensure_database_schema(engine)

    uow = unit_of_work or SqlAlchemyUnitOfWork(SessionLocal())
    resolved_id_generator = id_generator or IdGenerator()
    ingestion_input_limits = resolve_ingestion_input_limits()

    parsing_workflow, document_graph_builder = build_parsing_runtime(
        id_generator=resolved_id_generator,
    )

    llm_service = LLMService(
        OllamaLLMProvider(
            base_url=llm_settings.ollama_base_url,
            default_model=llm_settings.general_llm,
        )
    )
    resolved_embedding_provider = embedding_provider or create_embedding_provider()
    if vector_store is not None:
        resolved_vector_store = vector_store
        resolved_qdrant_client = qdrant_client
    else:
        resolved_vector_store, resolved_qdrant_client = build_vector_store(
            unit_of_work=uow,
            embedding_provider=resolved_embedding_provider,
        )
    embedding_workflow = build_embedding_workflow(
        vector_store=resolved_vector_store,
        embedding_provider=resolved_embedding_provider,
    )

    document_repository = uow.documents
    classification_repository = uow.classifications
    document_graph_validator = DocumentGraphValidator()
    document_validator = DocumentClassificationValidator()
    document_lookup_service = DocumentLookupService(document_repository)
    document_registration_service = DocumentRegistrationService(
        document_repository=document_repository,
        document_graph_validator=document_graph_validator,
    )
    duplicate_detection_service = DuplicateDetectionService(document_repository)

    classification_service = ClassificationService(
        classification_repository=classification_repository,
        document_classification_validator=document_validator,
    )
    document_classification_workflow = DocumentClassificationWorkflow(
        llm_service=llm_service,
        classification_service=classification_service,
        document_classification_validator=document_validator,
        id_generator=resolved_id_generator,
        document_repository=document_repository,
    )
    post_classification_chunk_finalization_workflow = (
        PostClassificationChunkFinalizationWorkflow(
            document_lookup_service=document_lookup_service,
            document_registration_service=document_registration_service,
            classification_service=classification_service,
            chunk_type_classification_workflow=ChunkTypeClassificationWorkflow(
                llm_service=llm_service,
            ),
            question_generation_service=QuestionGenerationService(
                llm_service=llm_service,
                id_generator=resolved_id_generator,
            ),
            embedding_workflow=embedding_workflow,
            vector_store=resolved_vector_store,
            graph_chunk_builder=document_graph_builder.chunk_builder,
        )
    )

    extraction_result_validator = ExtractionResultValidator()
    extraction_service = ExtractionService(
        extraction_repository=uow.extractions,
        extraction_result_validator=extraction_result_validator,
    )
    extraction_workflow = ExtractionWorkflow(
        llm_service=llm_service,
        extraction_service=extraction_service,
        extraction_result_validator=extraction_result_validator,
        id_generator=resolved_id_generator,
    )

    identifier_promotion_service = None
    deterministic_identifier_scanner = None
    if extraction_settings.identifier_extraction_enabled:
        identifier_promotion_service = IdentifierPromotionService(
            min_length=extraction_settings.identifier_min_length,
        )
        deterministic_identifier_scanner = DeterministicIdentifierScanner(
            min_length=extraction_settings.identifier_min_length,
        )

    semantic_linking_workflow = None
    if (
        extraction_settings.extraction_enabled
        and extraction_settings.semantic_linking_enabled
    ):
        semantic_linking_workflow = SemanticLinkingWorkflow(
            extraction_service=extraction_service,
            id_generator=resolved_id_generator,
            document_lookup_service=document_lookup_service,
        )
    runtime_capabilities = IngestionRuntimeProfileResolver().resolve(
        requested_profile=ingestion_settings.ingestion_runtime_profile,
        extraction_enabled=extraction_settings.extraction_enabled,
        question_generation_enabled=ingestion_settings.enable_question_generation,
        deterministic_identifier_scan_enabled=(
            extraction_settings.identifier_extraction_enabled
        ),
        semantic_linking_enabled=(
            extraction_settings.extraction_enabled
            and extraction_settings.semantic_linking_enabled
        ),
        classification_enabled=classification_settings.enabled,
    )

    ingestion_workflow = IngestionWorkflow(
        unit_of_work=uow,
        ingestion_request_validator=IngestionRequestValidator(
            max_file_size_bytes=ingestion_input_limits.max_file_size_bytes,
        ),
        duplicate_detection_service=duplicate_detection_service,
        parsing_workflow=parsing_workflow,
        document_registration_service=document_registration_service,
        document_classification_workflow=document_classification_workflow,
        post_classification_chunk_finalization_workflow=(
            post_classification_chunk_finalization_workflow
        ),
        extraction_workflow=extraction_workflow,
        embedding_workflow=embedding_workflow,
        id_generator=resolved_id_generator,
        runtime_capabilities=runtime_capabilities,
        extraction_enabled=extraction_settings.extraction_enabled,
        classification_enabled=classification_settings.enabled,
        identifier_promotion_service=identifier_promotion_service,
        deterministic_identifier_scanner=deterministic_identifier_scanner,
        document_lookup_service=document_lookup_service,
        semantic_linking_workflow=semantic_linking_workflow,
    )

    delete_document_workflow = DeleteDocumentWorkflow(
        unit_of_work=uow,
        vector_store=resolved_vector_store,
    )

    return IngestionRuntime(
        ingestion_workflow=ingestion_workflow,
        delete_document_workflow=delete_document_workflow,
        parsing_workflow=parsing_workflow,
        document_graph_builder=document_graph_builder,
        document_registration_service=document_registration_service,
        document_lookup_service=document_lookup_service,
        duplicate_detection_service=duplicate_detection_service,
        classification_service=classification_service,
        document_classification_workflow=document_classification_workflow,
        extraction_service=extraction_service,
        post_classification_chunk_finalization_workflow=(
            post_classification_chunk_finalization_workflow
        ),
        unit_of_work=uow,
        embedding_model=embedding_settings.model_name,
        vector_collection=qdrant_settings.collection,
        qdrant_client=resolved_qdrant_client,
    )
