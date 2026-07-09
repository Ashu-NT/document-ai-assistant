from __future__ import annotations

from types import SimpleNamespace

from src.application.orchestrator.retrieval import retrieval_runtime_builder
from src.application.orchestrator.retrieval.retrieval_runtime_builder import (
    build_retrieval_runtime,
)


class _FakeVectorStore:
    pass


def _fake_build_vector_store(*, unit_of_work, embedding_provider):
    return _FakeVectorStore(), SimpleNamespace(name="fake_qdrant_client")


def _uow() -> SimpleNamespace:
    return SimpleNamespace(
        documents="documents_repo",
        keyword_index="keyword_index_repo",
        extractions="extractions_repo",
        vector_mappings="vector_mappings_repo",
    )


def test_build_retrieval_runtime_wires_the_retrieval_stack(monkeypatch) -> None:
    monkeypatch.setattr(
        retrieval_runtime_builder, "build_vector_store", _fake_build_vector_store
    )
    embedding_provider = object()

    runtime = build_retrieval_runtime(
        unit_of_work=_uow(),
        embedding_provider=embedding_provider,
    )

    assert isinstance(runtime.vector_store, _FakeVectorStore)
    assert runtime.qdrant_client.name == "fake_qdrant_client"
    assert runtime.embedding_provider is embedding_provider
    assert runtime.retrieval_workflow.retrieval_service.vector_store is runtime.vector_store
    assert runtime.retrieval_workflow.context_expander.document_lookup_service is (
        runtime.document_lookup_service
    )
    assert runtime.retrieval_workflow.structured_evidence_resolver is not None
    assert runtime.exploration_service.document_lookup_service is runtime.document_lookup_service


def test_build_retrieval_runtime_builds_a_fresh_embedding_provider_when_not_given(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        retrieval_runtime_builder, "build_vector_store", _fake_build_vector_store
    )
    sentinel_provider = object()
    monkeypatch.setattr(
        retrieval_runtime_builder, "create_embedding_provider", lambda: sentinel_provider
    )

    runtime = build_retrieval_runtime(unit_of_work=_uow())

    assert runtime.embedding_provider is sentinel_provider


def test_build_retrieval_runtime_defaults_guardrails_to_empty_lists(monkeypatch) -> None:
    monkeypatch.setattr(
        retrieval_runtime_builder, "build_vector_store", _fake_build_vector_store
    )

    runtime = build_retrieval_runtime(unit_of_work=_uow(), embedding_provider=object())

    assert runtime.retrieval_workflow.pre_retrieval_guardrails == []
    assert runtime.retrieval_workflow.post_retrieval_guardrails == []


def test_build_retrieval_runtime_passes_through_provided_guardrails(monkeypatch) -> None:
    monkeypatch.setattr(
        retrieval_runtime_builder, "build_vector_store", _fake_build_vector_store
    )
    pre_guardrail = object()
    post_guardrail_a = object()
    post_guardrail_b = object()

    runtime = build_retrieval_runtime(
        unit_of_work=_uow(),
        embedding_provider=object(),
        pre_retrieval_guardrails=[pre_guardrail],
        post_retrieval_guardrails=[post_guardrail_a, post_guardrail_b],
    )

    assert runtime.retrieval_workflow.pre_retrieval_guardrails == [pre_guardrail]
    assert runtime.retrieval_workflow.post_retrieval_guardrails == [
        post_guardrail_a,
        post_guardrail_b,
    ]
