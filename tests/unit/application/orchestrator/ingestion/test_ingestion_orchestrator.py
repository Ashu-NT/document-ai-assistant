from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.application.orchestrator.ingestion import ingestion_orchestrator
from src.application.orchestrator.ingestion.ingestion_orchestrator import (
    build_ingestion_runtime,
)


class _Recorder:
    """Generic fake constructor that just remembers how it was called."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def _fake_uow():
    return SimpleNamespace(
        documents="documents_repo",
        classifications="classifications_repo",
        extractions="extractions_repo",
        vector_mappings="vector_mappings_repo",
    )


@pytest.fixture()
def patched(monkeypatch):
    """Patch every external/heavy dependency the orchestrator wires together."""
    calls: dict[str, list] = {"bootstrap_application": [], "ensure_database_schema": []}

    monkeypatch.setattr(
        ingestion_orchestrator,
        "bootstrap_application",
        lambda: calls["bootstrap_application"].append(True),
    )
    monkeypatch.setattr(
        ingestion_orchestrator,
        "ensure_database_schema",
        lambda engine: calls["ensure_database_schema"].append(engine),
    )
    monkeypatch.setattr(ingestion_orchestrator, "engine", "fake_engine")
    monkeypatch.setattr(ingestion_orchestrator, "SessionLocal", lambda: "fake_session")
    monkeypatch.setattr(ingestion_orchestrator, "SqlAlchemyUnitOfWork", lambda session: _fake_uow())

    monkeypatch.setattr(
        ingestion_orchestrator,
        "build_parsing_runtime",
        lambda *, id_generator: ("fake_parsing_workflow", SimpleNamespace(chunk_builder="chunk_builder")),
    )
    monkeypatch.setattr(ingestion_orchestrator, "LLMService", _Recorder)
    monkeypatch.setattr(ingestion_orchestrator, "OllamaLLMProvider", _Recorder)
    monkeypatch.setattr(ingestion_orchestrator, "create_embedding_provider", lambda: "fake_embedding_provider")
    monkeypatch.setattr(
        ingestion_orchestrator,
        "build_vector_store",
        lambda *, unit_of_work, embedding_provider: ("fake_vector_store", "fake_qdrant_client"),
    )
    monkeypatch.setattr(
        ingestion_orchestrator,
        "build_embedding_workflow",
        lambda *, vector_store, embedding_provider: "fake_embedding_workflow",
    )

    for name in (
        "DocumentGraphValidator",
        "DocumentClassificationValidator",
        "ChunkClassificationValidator",
        "DocumentLookupService",
        "DocumentRegistrationService",
        "DuplicateDetectionService",
        "ClassificationService",
        "ChunkClassificationWorkflow",
        "DocumentClassificationWorkflow",
        "ChunkTypeClassificationWorkflow",
        "QuestionGenerationService",
        "PostClassificationChunkFinalizationWorkflow",
        "ExtractionResultValidator",
        "ExtractionService",
        "ExtractionWorkflow",
        "IdentifierPromotionService",
        "DeterministicIdentifierScanner",
        "IngestionRequestValidator",
        "IngestionWorkflow",
        "DeleteDocumentWorkflow",
    ):
        monkeypatch.setattr(ingestion_orchestrator, name, _Recorder)

    monkeypatch.setattr(
        ingestion_orchestrator.embedding_settings, "model_name", "bge-small", raising=False
    )
    monkeypatch.setattr(
        ingestion_orchestrator.qdrant_settings, "collection", "document_chunks", raising=False
    )
    monkeypatch.setattr(
        ingestion_orchestrator.extraction_settings,
        "identifier_extraction_enabled",
        True,
        raising=False,
    )
    monkeypatch.setattr(
        ingestion_orchestrator.extraction_settings, "identifier_min_length", 3, raising=False
    )

    return calls


def test_bootstrap_runs_by_default(patched):
    build_ingestion_runtime()

    assert patched["bootstrap_application"] == [True]
    assert patched["ensure_database_schema"] == ["fake_engine"]


def test_bootstrap_skipped_when_disabled(patched):
    build_ingestion_runtime(bootstrap=False)

    assert patched["bootstrap_application"] == []
    assert patched["ensure_database_schema"] == []


def test_uses_provided_unit_of_work_instead_of_constructing_one(monkeypatch, patched):
    calls = []
    monkeypatch.setattr(
        ingestion_orchestrator,
        "SqlAlchemyUnitOfWork",
        lambda session: calls.append(session) or _fake_uow(),
    )
    provided_uow = _fake_uow()

    runtime = build_ingestion_runtime(unit_of_work=provided_uow)

    assert calls == []
    assert runtime.unit_of_work is provided_uow


def test_constructs_unit_of_work_when_not_provided(patched):
    runtime = build_ingestion_runtime()

    assert runtime.unit_of_work is not None


def test_uses_provided_id_generator_consistently(patched):
    sentinel_id_generator = object()

    runtime = build_ingestion_runtime(id_generator=sentinel_id_generator)

    assert runtime.ingestion_workflow.kwargs["id_generator"] is sentinel_id_generator


def test_identifier_services_wired_when_enabled(patched):
    runtime = build_ingestion_runtime()

    ingestion_workflow = runtime.ingestion_workflow
    assert isinstance(ingestion_workflow, _Recorder)
    promotion_service = ingestion_workflow.kwargs["identifier_promotion_service"]
    scanner = ingestion_workflow.kwargs["deterministic_identifier_scanner"]

    assert isinstance(promotion_service, _Recorder)
    assert promotion_service.kwargs == {"min_length": 3}
    assert isinstance(scanner, _Recorder)
    assert scanner.kwargs == {"min_length": 3}


def test_identifier_services_are_none_when_disabled(monkeypatch, patched):
    monkeypatch.setattr(
        ingestion_orchestrator.extraction_settings,
        "identifier_extraction_enabled",
        False,
        raising=False,
    )

    runtime = build_ingestion_runtime()

    ingestion_workflow = runtime.ingestion_workflow
    assert ingestion_workflow.kwargs["identifier_promotion_service"] is None
    assert ingestion_workflow.kwargs["deterministic_identifier_scanner"] is None


def test_runtime_fields_are_populated(patched):
    runtime = build_ingestion_runtime()

    assert isinstance(runtime.ingestion_workflow, _Recorder)
    assert runtime.parsing_workflow == "fake_parsing_workflow"
    assert isinstance(runtime.document_graph_builder, SimpleNamespace)
    assert isinstance(runtime.document_registration_service, _Recorder)
    assert isinstance(runtime.document_lookup_service, _Recorder)
    assert isinstance(runtime.duplicate_detection_service, _Recorder)
    assert isinstance(runtime.classification_service, _Recorder)
    assert isinstance(runtime.document_classification_workflow, _Recorder)
    assert isinstance(runtime.post_classification_chunk_finalization_workflow, _Recorder)
    assert runtime.embedding_model == "bge-small"
    assert runtime.vector_collection == "document_chunks"
    assert runtime.qdrant_client == "fake_qdrant_client"


def test_ingestion_workflow_reuses_the_same_extraction_workflow(patched):
    runtime = build_ingestion_runtime()

    extraction_workflow = runtime.ingestion_workflow.kwargs["extraction_workflow"]
    assert isinstance(extraction_workflow, _Recorder)


def test_ingestion_workflow_is_wired_with_the_same_document_lookup_service(patched):
    runtime = build_ingestion_runtime()

    assert (
        runtime.ingestion_workflow.kwargs["document_lookup_service"]
        is runtime.document_lookup_service
    )


def test_post_classification_workflow_uses_the_document_graph_builder_chunk_builder(patched):
    runtime = build_ingestion_runtime()

    post_classification_kwargs = runtime.post_classification_chunk_finalization_workflow.kwargs
    assert post_classification_kwargs["graph_chunk_builder"] == "chunk_builder"


def test_delete_document_workflow_is_wired_with_the_same_unit_of_work_and_vector_store(
    patched,
):
    runtime = build_ingestion_runtime()

    assert isinstance(runtime.delete_document_workflow, _Recorder)
    assert runtime.delete_document_workflow.kwargs["unit_of_work"] is runtime.unit_of_work
    assert runtime.delete_document_workflow.kwargs["vector_store"] == "fake_vector_store"


def test_reuses_a_provided_vector_store_instead_of_building_a_new_one(monkeypatch, patched):
    calls = []
    monkeypatch.setattr(
        ingestion_orchestrator,
        "build_vector_store",
        lambda **kwargs: calls.append(kwargs) or ("should_not_be_used", "should_not_be_used"),
    )
    sentinel_vector_store = object()
    sentinel_qdrant_client = object()
    sentinel_embedding_provider = object()

    runtime = build_ingestion_runtime(
        vector_store=sentinel_vector_store,
        qdrant_client=sentinel_qdrant_client,
        embedding_provider=sentinel_embedding_provider,
    )

    assert calls == []
    assert runtime.qdrant_client is sentinel_qdrant_client
    assert (
        runtime.delete_document_workflow.kwargs["vector_store"]
        is sentinel_vector_store
    )
    assert (
        runtime.ingestion_workflow.kwargs["post_classification_chunk_finalization_workflow"]
        .kwargs["vector_store"]
        is sentinel_vector_store
    )
