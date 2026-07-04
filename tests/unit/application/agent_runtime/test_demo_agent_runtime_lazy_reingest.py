from types import SimpleNamespace

from src.application.agent_runtime.demo_agent_runtime import _LazyIngestionWorkflow


def test_lazy_ingestion_workflow_does_not_build_until_called(monkeypatch) -> None:
    calls = []

    def _fake_build_ingestion_runtime(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(ingestion_workflow=_FakeIngestionWorkflow())

    monkeypatch.setattr(
        "src.application.orchestrator.ingestion.build_ingestion_runtime",
        _fake_build_ingestion_runtime,
    )

    _LazyIngestionWorkflow(
        unit_of_work="uow",
        vector_store="vector_store",
        qdrant_client="qdrant_client",
        embedding_provider="embedding_provider",
    )

    assert calls == []


class _FakeIngestionWorkflow:
    def __init__(self) -> None:
        self.run_calls = []
        self.reingest_calls = []

    def run(self, request):
        self.run_calls.append(request)
        return "run_result"

    def reingest(self, request):
        self.reingest_calls.append(request)
        return "reingest_result"


def test_lazy_ingestion_workflow_builds_once_and_reuses_the_same_ingestion_workflow(
    monkeypatch,
) -> None:
    calls = []
    fake_ingestion_workflow = _FakeIngestionWorkflow()

    def _fake_build_ingestion_runtime(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(ingestion_workflow=fake_ingestion_workflow)

    monkeypatch.setattr(
        "src.application.orchestrator.ingestion.build_ingestion_runtime",
        _fake_build_ingestion_runtime,
    )

    lazy = _LazyIngestionWorkflow(
        unit_of_work="uow",
        vector_store="vector_store",
        qdrant_client="qdrant_client",
        embedding_provider="embedding_provider",
    )

    result_1 = lazy.reingest("request_1")
    result_2 = lazy.reingest("request_2")

    assert result_1 == "reingest_result"
    assert result_2 == "reingest_result"
    assert fake_ingestion_workflow.reingest_calls == ["request_1", "request_2"]
    # build_ingestion_runtime must only be called once, on the first reingest.
    assert len(calls) == 1
    assert calls[0] == {
        "unit_of_work": "uow",
        "vector_store": "vector_store",
        "qdrant_client": "qdrant_client",
        "embedding_provider": "embedding_provider",
        "bootstrap": False,
    }


def test_lazy_ingestion_workflow_run_and_reingest_share_the_same_build(
    monkeypatch,
) -> None:
    calls = []
    fake_ingestion_workflow = _FakeIngestionWorkflow()

    def _fake_build_ingestion_runtime(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(ingestion_workflow=fake_ingestion_workflow)

    monkeypatch.setattr(
        "src.application.orchestrator.ingestion.build_ingestion_runtime",
        _fake_build_ingestion_runtime,
    )

    lazy = _LazyIngestionWorkflow(
        unit_of_work="uow",
        vector_store="vector_store",
        qdrant_client="qdrant_client",
        embedding_provider="embedding_provider",
    )

    run_result = lazy.run("ingest_request")
    reingest_result = lazy.reingest("reingest_request")

    assert run_result == "run_result"
    assert reingest_result == "reingest_result"
    assert fake_ingestion_workflow.run_calls == ["ingest_request"]
    assert fake_ingestion_workflow.reingest_calls == ["reingest_request"]
    # A single shared IngestionWorkflow build serves both the ingest and
    # reingest tools, regardless of which one triggers it first.
    assert len(calls) == 1
