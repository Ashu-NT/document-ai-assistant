from src.application.langgraph.graphs.document_agent import document_agent_graph_builder
from src.config.settings import langgraph_settings


class _FakeCompiledGraph:
    pass


class _FakeStateGraph:
    def __init__(self, _state_type) -> None:
        pass

    def add_node(self, *_args, **_kwargs) -> None:
        pass

    def add_edge(self, *_args, **_kwargs) -> None:
        pass

    def add_conditional_edges(self, *_args, **_kwargs) -> None:
        pass

    def compile(self):
        return _FakeCompiledGraph()


def test_compile_graph_returns_none_when_langgraph_disabled(monkeypatch) -> None:
    monkeypatch.setattr(document_agent_graph_builder, "StateGraph", _FakeStateGraph)
    monkeypatch.setattr(langgraph_settings, "enabled", False)

    result = document_agent_graph_builder.compile_graph({})

    assert result is None


def test_compile_graph_compiles_when_langgraph_enabled(monkeypatch) -> None:
    monkeypatch.setattr(document_agent_graph_builder, "StateGraph", _FakeStateGraph)
    monkeypatch.setattr(langgraph_settings, "enabled", True)

    result = document_agent_graph_builder.compile_graph({})

    assert isinstance(result, _FakeCompiledGraph)


def test_compile_graph_returns_none_when_state_graph_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(document_agent_graph_builder, "StateGraph", None)
    monkeypatch.setattr(langgraph_settings, "enabled", True)

    result = document_agent_graph_builder.compile_graph({})

    assert result is None
