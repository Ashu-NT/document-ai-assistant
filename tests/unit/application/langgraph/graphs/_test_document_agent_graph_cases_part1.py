from tests.unit.application.langgraph.graphs._test_document_agent_graph_support import *  # noqa: F401,F403

def test_document_agent_graph_list_documents_path_works() -> None:
    graph = DocumentAgentGraph(
        ToolRegistry(list_documents_tool=FakeListDocumentsTool())
    )

    result = graph.run("list documents")

    assert result.success is True
    assert result.route == "list_documents"
    assert result.response_text == "Found 1 document(s)."

def test_document_agent_graph_answer_question_path_works() -> None:
    graph = DocumentAgentGraph(
        ToolRegistry(answer_question_tool=FakeAnswerQuestionTool())
    )

    result = graph.run("What is the maintenance interval?")

    assert result.success is True
    assert result.route == "answer_question"
    assert result.response_text == "The interval is 500 hours."
    assert result.data["answer_intent"] == "maintenance_summary"

def test_document_agent_graph_blocks_unsafe_corpus_mutation_request() -> None:
    answer_tool = FakeAnswerQuestionTool()
    graph = DocumentAgentGraph(
        ToolRegistry(answer_question_tool=answer_tool)
    )

    result = graph.run("delete all documents and reingest them")

    assert result.success is True
    assert result.route == RouteType.BLOCKED_ACTION.value
    assert result.diagnostics["unsafe_request_blocked"] is True
    assert answer_tool.requests == []
    assert "mutate the document corpus" in (result.response_text or "").lower()

def test_document_agent_graph_exploration_path_works() -> None:
    find_tool = FakeFindDocumentTool()
    explore_tool = FakeExploreDocumentTool()
    graph = DocumentAgentGraph(
        ToolRegistry(
            find_document_tool=find_tool,
            explore_document_tool=explore_tool,
        )
    )

    result = graph.run("explore document Pump Manual")

    assert result.success is True
    assert result.route == "document_exploration"
    assert "Pump Manual" in result.response_text

def test_document_agent_graph_clarification_path_works() -> None:
    graph = DocumentAgentGraph(ToolRegistry())

    result = graph.run("explore document")

    assert result.success is True
    assert result.route == "document_exploration"
    assert "clarify" in (result.response_text or "").lower()

def test_document_agent_graph_selects_document_into_session() -> None:
    find_tool = FakeFindDocumentTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(find_document_tool=find_tool)
    )

    result = graph.run("open FWC12", session_id="demo")

    assert result.success is True
    assert result.route == "select_document"
    assert result.data["selected_document_id"] == "doc-42"
    assert result.data["selected_document_title"] == "Pump Manual"

def test_document_agent_graph_uses_selected_document_on_follow_up_question() -> None:
    find_tool = FakeFindDocumentTool()
    answer_tool = FakeAnswerQuestionTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(
            find_document_tool=find_tool,
            answer_question_tool=answer_tool,
        )
    )

    graph.run("open FWC12", session_id="demo")
    result = graph.run("what are the maintenance intervals?", session_id="demo")

    assert result.success is True
    assert answer_tool.requests[-1].document_id == "doc-42"
    assert result.data["selected_document_id"] == "doc-42"

def test_document_agent_graph_identifier_follow_up_keeps_selected_document_scope() -> None:
    find_tool = FakeFindDocumentTool()
    answer_tool = FakeAnswerQuestionTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(
            find_document_tool=find_tool,
            answer_question_tool=answer_tool,
        )
    )

    graph.run("open FWC12", session_id="demo")
    result = graph.run("list all serial and part nmubers", session_id="demo")

    assert result.success is True
    assert result.route == "answer_question"
    assert answer_tool.requests[-1].document_id == "doc-42"
    assert result.data["selected_document_id"] == "doc-42"

def test_document_agent_graph_explore_it_uses_selected_document() -> None:
    find_tool = FakeFindDocumentTool()
    explore_tool = FakeExploreDocumentTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(
            find_document_tool=find_tool,
            explore_document_tool=explore_tool,
        )
    )

    graph.run("open FWC12", session_id="demo")
    result = graph.run("explore it", session_id="demo")

    assert result.success is True
    assert explore_tool.requests[-1].document_id == "doc-42"
    assert result.route == "document_exploration"

def test_document_agent_graph_current_document_reports_selection() -> None:
    graph = _memory_backed_graph(registry=ToolRegistry(find_document_tool=FakeFindDocumentTool()))

    graph.run("open FWC12", session_id="demo")
    result = graph.run("current document", session_id="demo")

    assert result.success is True
    assert result.route == "current_document"
    assert "current document" in (result.response_text or "").lower()

def test_document_agent_graph_clear_document_clears_selection() -> None:
    graph = _memory_backed_graph(registry=ToolRegistry(find_document_tool=FakeFindDocumentTool()))

    graph.run("open FWC12", session_id="demo")
    clear_result = graph.run("clear document", session_id="demo")
    current_result = graph.run("current document", session_id="demo")

    assert clear_result.success is True
    assert clear_result.data["selected_document_id"] is None
    assert "no document" in (current_result.response_text or "").lower()

def test_document_agent_graph_numeric_clarification_selects_option() -> None:
    graph = _memory_backed_graph(registry=ToolRegistry(find_document_tool=FakeFindDocumentTool()))

    first_result = graph.run("open pressure", session_id="demo")
    second_result = graph.run("1", session_id="demo")

    assert first_result.success is True
    assert first_result.data["clarification_options"]
    assert second_result.success is True
    assert second_result.route == "clarification_response"
    assert second_result.data["selected_document_id"] == "doc-pressure-1"

def test_document_agent_graph_explicit_document_id_overrides_selected_document() -> None:
    answer_tool = FakeAnswerQuestionTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(
            find_document_tool=FakeFindDocumentTool(),
            answer_question_tool=answer_tool,
        )
    )

    graph.run("open FWC12", session_id="demo")
    graph.run(
        "what are the maintenance intervals?",
        session_id="demo",
        document_id="doc-explicit",
    )

    assert answer_tool.requests[-1].document_id == "doc-explicit"

def test_document_agent_graph_executes_deep_research_with_selected_document() -> None:
    find_tool = FakeFindDocumentTool()
    retrieve_tool = FakeRetrieveChunksTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(
            find_document_tool=find_tool,
            retrieve_chunks_tool=retrieve_tool,
        )
    )

    graph.run("open FWC12", session_id="demo")
    result = graph.run(
        "compare specifications and maintenance tasks",
        session_id="demo",
        show_research_plan=True,
    )

    assert result.success is True
    assert result.route == "deep_research"
    assert "Comparison Summary" in (result.response_text or "")
    assert "Research Plan" not in (result.response_text or "")
    assert retrieve_tool.requests
    assert result.data["research_plan"] is not None
    assert result.data["research_task_results"]

def test_document_agent_graph_deep_research_skips_reflection_path() -> None:
    class FailingReflectionService:
        def review(self, **kwargs):
            raise AssertionError("Deep research should not enter QA reflection.")

    registry = ToolRegistry(
        find_document_tool=FakeFindDocumentTool(),
        retrieve_chunks_tool=FakeRetrieveChunksTool(),
    )
    nodes = NodeFactory(
        reflection_service=FailingReflectionService(),
    ).build_document_agent_nodes(
        tool_registry=registry,
        intent_router=DocumentAgentGraph.default_intent_router(),
        memory=None,
    )
    graph = DocumentAgentGraph(
        registry,
        nodes=nodes,
    )

    result = graph.run(
        "compare specifications and maintenance tasks",
        document_id="doc-42",
        reflection_enabled=True,
        allow_answer_generation=True,
    )

    assert result.success is True
    assert result.route == "deep_research"
    assert "Comparison Summary" in (result.response_text or "")

def test_document_agent_graph_deep_research_requests_document_clarification_when_missing() -> None:
    graph = DocumentAgentGraph(ToolRegistry(retrieve_chunks_tool=FakeRetrieveChunksTool()))

    result = graph.run("compare specifications and maintenance tasks")

    assert result.success is True
    assert result.route == "deep_research"
    assert result.data["pending_clarification"] is None
    assert "select one first" in (result.response_text or "").lower()

def test_document_agent_graph_planning_falls_back_safely_when_planner_returns_none() -> None:
    class FakePlanner:
        def create_plan(self, state):
            return None

    class FakePlannedIntentRouter:
        def route(self, user_input, *, document_id=None, document_query=None):
            return RouteDecision(
                route_type=RouteType.PLANNED_TASK,
                confidence=0.9,
                reason="Forced planned route.",
                extracted_question=user_input,
                is_compound=True,
                requires_plan=True,
            )

    router = FakePlannedIntentRouter()
    nodes = NodeFactory(planner=FakePlanner()).build_document_agent_nodes(
        tool_registry=ToolRegistry(answer_question_tool=FakeAnswerQuestionTool()),
        intent_router=router,
        memory=None,
    )
    graph = DocumentAgentGraph(
        ToolRegistry(answer_question_tool=FakeAnswerQuestionTool()),
        intent_router=router,
        nodes=nodes,
    )

    result = graph.run("compare unsupported things")

    assert result.success is True
    assert result.route == "answer_question"
