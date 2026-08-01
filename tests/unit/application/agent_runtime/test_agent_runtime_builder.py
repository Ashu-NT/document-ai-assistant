from types import SimpleNamespace

from src.application.agent_runtime.bootstrap.agent_runtime_builder import (
    build_agent_runtime,
)
from src.config.settings import memory_settings


class _FakeDocumentCatalogService:
    def list_documents(self):
        return []


class _FakeServices:
    document_catalog_service = _FakeDocumentCatalogService()
    qdrant_client = None


class _FakeGraphFactory:
    def __init__(self, *, node_factory=None) -> None:
        self.node_factory = node_factory

    def create_document_agent_graph(self, *, tool_registry, memory=None, **_kwargs):
        return SimpleNamespace(tool_registry=tool_registry, memory=memory)


def _patch_heavy_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.application.agent_runtime.bootstrap.agent_runtime_builder.build_agent_services",
        lambda *args, **kwargs: _FakeServices(),
    )
    monkeypatch.setattr(
        "src.application.agent_runtime.bootstrap.agent_runtime_builder.build_agent_tool_registry",
        lambda services: "fake_tool_registry",
    )
    monkeypatch.setattr(
        "src.application.agent_runtime.bootstrap.agent_runtime_builder.build_agent_node_factory",
        lambda services, **kwargs: "fake_node_factory",
    )
    monkeypatch.setattr(
        "src.application.langgraph.GraphFactory",
        _FakeGraphFactory,
    )


def test_build_agent_runtime_yields_no_conversation_memory_when_disabled(monkeypatch) -> None:
    _patch_heavy_dependencies(monkeypatch)
    monkeypatch.setattr(memory_settings, "enable_short_term_memory", False)

    runtime = build_agent_runtime(
        session="fake_session",
        enable_generation=False,
        enable_llm_planning=False,
        enable_llm_research_planning=False,
    )

    assert runtime.conversation_memory is None
    assert runtime.graph.memory is None


def test_build_agent_runtime_builds_conversation_memory_when_enabled(monkeypatch) -> None:
    _patch_heavy_dependencies(monkeypatch)
    monkeypatch.setattr(memory_settings, "enable_short_term_memory", True)

    runtime = build_agent_runtime(
        session="fake_session",
        enable_generation=False,
        enable_llm_planning=False,
        enable_llm_research_planning=False,
    )

    assert runtime.conversation_memory is not None
    assert runtime.graph.memory is runtime.conversation_memory
