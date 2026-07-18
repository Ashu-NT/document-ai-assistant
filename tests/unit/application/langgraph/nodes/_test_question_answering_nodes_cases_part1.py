from tests.unit.application.langgraph.nodes._test_question_answering_nodes_support import *  # noqa: F401,F403

def test_answer_question_node_calls_tool_with_document_id() -> None:
    tool = FakeAnswerQuestionTool()
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=tool))

    patch = node(
        build_agent_state(
            user_input="What is the maintenance interval?",
            document_id="doc-42",
        )
    )

    assert tool.requests[0].document_id == "doc-42"
    assert patch["response_text"] == "Generated answer."

def test_explore_document_node_requires_document_id() -> None:
    node = ExploreDocumentNode(ToolRegistry())

    patch = node(build_agent_state(user_input="explore document"))

    assert patch["needs_clarification"] is True

def test_retrieve_evidence_node_calls_retrieve_chunks_tool() -> None:
    tool = FakeRetrieveChunksTool()
    node = RetrieveEvidenceNode(ToolRegistry(retrieve_chunks_tool=tool))

    patch = node(
        build_agent_state(
            user_input="retrieve shaft seal lubrication",
            document_id="doc-42",
            top_k=3,
        )
    )

    assert tool.requests[0].document_id == "doc-42"
    assert tool.requests[0].top_k == 3
    assert "Retrieved 1 evidence chunk" in patch["response_text"]

def test_answer_question_node_uses_selected_document_when_request_document_missing() -> None:
    tool = FakeAnswerQuestionTool()
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=tool))

    node(
        build_agent_state(
            user_input="What is the maintenance interval?",
            selected_document_id="doc-selected",
            selected_document_title="FWC12 Manual",
        )
    )

    assert tool.requests[0].document_id == "doc-selected"

def test_retrieve_evidence_node_uses_strategy_selected_table_tool_when_requested() -> None:
    chunk_tool = FakeRetrieveChunksTool()
    table_tool = FakeRetrieveTablesTool()
    node = RetrieveEvidenceNode(
        ToolRegistry(
            retrieve_chunks_tool=chunk_tool,
            retrieve_tables_tool=table_tool,
        ),
        retrieval_strategy_service=RetrievalStrategyService(),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=RetrievalStrategyPolicy(enabled=True),
    )

    patch = node(
        build_agent_state(
            user_input="show maintenance table",
            document_id="doc-42",
            top_k=3,
            retrieval_strategy_enabled=True,
            requested_retrieval_strategy="table",
        )
    )

    assert table_tool.requests
    assert patch["retrieval_strategy_decision"]["primary_strategy"] == "TABLE_LOOKUP"
    assert "Retrieved 1 evidence chunk" in patch["response_text"]

def test_answer_question_node_passes_strategy_selected_chunks_as_override() -> None:
    answer_tool = FakeAnswerQuestionTool()
    table_tool = FakeRetrieveTablesTool()
    node = AnswerQuestionNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=FakeRetrieveChunksTool(),
            retrieve_tables_tool=table_tool,
        ),
        retrieval_strategy_service=RetrievalStrategyService(),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=RetrievalStrategyPolicy(enabled=True),
    )

    node(
        build_agent_state(
            user_input="show maintenance table",
            document_id="doc-42",
            retrieval_strategy_enabled=True,
            requested_retrieval_strategy="table",
        )
    )

    assert table_tool.requests
    assert answer_tool.requests[0].context_override_chunks is not None
    assert len(answer_tool.requests[0].context_override_chunks) == 1

def test_answer_question_node_passes_strategy_resolved_identifiers_into_qa_request() -> None:
    answer_tool = FakeAnswerQuestionTool()
    identifier_tool = FakeRetrieveIdentifiersTool()
    node = AnswerQuestionNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_identifiers_tool=identifier_tool,
        ),
        retrieval_strategy_service=RetrievalStrategyService(),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=RetrievalStrategyPolicy(enabled=True),
    )

    patch = node(
        build_agent_state(
            user_input="list all serial and part nmubers",
            document_id="doc-42",
            retrieval_strategy_enabled=True,
            requested_retrieval_strategy="identifier",
        )
    )

    assert identifier_tool.requests
    assert len(answer_tool.requests[0].resolved_identifiers) == 1
    assert answer_tool.requests[0].resolved_identifiers[0].raw_value == "PN-001"
    assert patch["resolved_identifiers"][0]["raw_value"] == "PN-001"

def test_answer_question_node_surfaces_workflow_resolved_structured_entities() -> None:
    answer_tool = FakeAnswerQuestionTool(
        qa_result=FakeQAResult(
            answer_text="Generated answer.",
            resolved_structured_entities=[
                {
                    "name": "ACME Corp",
                    "website": "https://acme.example",
                    "_entity_type": "manufacturer",
                }
            ],
        )
    )
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=answer_tool))

    patch = node(
        build_agent_state(
            user_input="what is the manufacturer website",
            document_id="doc-42",
        )
    )

    assert patch["resolved_structured_entities"][0]["website"] == "https://acme.example"

def test_answer_question_node_does_not_require_direct_structured_lookup_tool() -> None:
    answer_tool = FakeAnswerQuestionTool()
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=answer_tool))

    node(
        build_agent_state(
            user_input="What is the maintenance interval?",
            document_id="doc-42",
        )
    )

    assert answer_tool.requests[0].resolved_structured_entities == []

def test_retry_retrieval_node_preserves_existing_structured_entities_for_regeneration() -> None:
    answer_tool = FakeAnswerQuestionTool()
    retry_tool = FakeRetryRetrieveChunksTool()
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=retry_tool,
        )
    )

    state = build_agent_state(
        user_input="what is the manufacturer website",
        document_id="doc-42",
        selected_document_id="doc-42",
        allow_answer_generation=True,
        include_context=True,
    )
    state["question"] = "what is the manufacturer website"
    state["route"] = "answer_question"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "Generic answer.",
            },
        }
    }
    state["reflection_result"] = {
        "decision": {
            "decision": "RETRIEVE_AGAIN",
            "reason": "Need the manufacturer website explicitly.",
        }
    }
    state["retry_query"] = "manufacturer website"
    state["initial_context_chunks"] = []
    state["resolved_structured_entities"] = [
        {
            "name": "ACME Corp",
            "website": "https://acme.example",
            "_entity_type": "manufacturer",
        }
    ]

    patch = node(state)

    assert len(answer_tool.requests[0].resolved_structured_entities) == 1
    assert patch["resolved_structured_entities"][0]["website"] == "https://acme.example"

def test_retry_retrieval_node_preserves_resolved_identifiers_for_regeneration() -> None:
    answer_tool = FakeAnswerQuestionTool()
    retry_tool = FakeRetryRetrieveChunksTool()
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=retry_tool,
        )
    )

    state = build_agent_state(
        user_input="list all serial and part nmubers",
        document_id="doc-42",
        selected_document_id="doc-42",
        allow_answer_generation=True,
        include_context=True,
    )
    state["question"] = "list all serial and part nmubers"
    state["route"] = "answer_question"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "Generic answer.",
                "answer_intent": "identifier_lookup",
            },
        }
    }
    state["reflection_result"] = {
        "decision": {
            "decision": "RETRIEVE_AGAIN",
            "reason": "Need explicit identifier values.",
        }
    }
    state["retry_query"] = "serial number part number identifier list"
    state["resolved_identifiers"] = [
        {
            "identifier_id": "identifier-1",
            "document_id": "doc-42",
            "raw_value": "PN-001",
            "identifier_type": "part_number",
        }
    ]
    state["initial_context_chunks"] = []

    patch = node(state)

    assert retry_tool.requests
    assert len(answer_tool.requests[0].resolved_identifiers) == 1
    assert answer_tool.requests[0].resolved_identifiers[0].raw_value == "PN-001"
    assert patch["resolved_identifiers"][0]["raw_value"] == "PN-001"


def _retry_state_with_stale_reflection_result() -> dict:
    state = build_agent_state(
        user_input="what is the manufacturer website",
        document_id="doc-42",
        selected_document_id="doc-42",
        allow_answer_generation=True,
        include_context=True,
    )
    state["question"] = "what is the manufacturer website"
    state["route"] = "answer_question"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {"route": "retrieval_qa", "answer_text": "Generic answer."},
        }
    }
    # The PREVIOUS reflection pass's result -- this must not survive a
    # failed retry to be shown to the user as if it described the retry.
    state["reflection_result"] = {
        "decision": {"decision": "RETRIEVE_AGAIN", "reason": "Need the manufacturer website."},
        "overall_score": 0.4,
    }
    state["reflection_score"] = 0.4
    state["retry_query"] = "manufacturer website"
    state["initial_context_chunks"] = []
    return state


class FakeFailingRetrieveChunksTool:
    def run(self, request):
        return ToolResult.fail("Retrieval backend unavailable.", error_code="retrieval_failed")


def test_retry_retrieval_node_clears_stale_reflection_result_when_retrieve_tool_fails() -> None:
    answer_tool = FakeAnswerQuestionTool()
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=FakeFailingRetrieveChunksTool(),
        )
    )

    patch = node(_retry_state_with_stale_reflection_result())

    assert patch["reflection_decision"] == "FAIL"
    assert patch["reflection_result"] is None
    assert patch["reflection_score"] is None


class FakeFailingAnswerQuestionTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.fail("Answer generation failed.", error_code="generation_failed")


def test_retry_retrieval_node_clears_stale_reflection_result_when_regeneration_fails() -> None:
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=FakeFailingAnswerQuestionTool(),
            retrieve_chunks_tool=FakeRetryRetrieveChunksTool(),
        )
    )

    patch = node(_retry_state_with_stale_reflection_result())

    assert patch["reflection_decision"] == "FAIL"
    assert patch["reflection_result"] is None
    assert patch["reflection_score"] is None


class FakeMultiStrategyRetryPolicy:
    """Returns a fixed multi-strategy recommendation regardless of input,
    standing in for StrategyRetryPolicy's keyword matching so the test
    doesn't depend on exact wording."""

    def recommend(self, *, retry_reason, retry_query, initial_primary_strategy):
        from src.application.langgraph.retrieval_strategy import RetrievalStrategy

        return [RetrievalStrategy.MAINTENANCE_LOOKUP, RetrievalStrategy.TABLE_LOOKUP]


def test_retry_retrieval_node_honors_a_multi_strategy_recommendation() -> None:
    # Regression guard: StrategyRetryPolicy.recommend() returning more than
    # one strategy (its actual "diversify on retry" signal) previously fell
    # through to the same deterministic scoring as a non-retry request,
    # silently discarding the recommendation -- only a single-strategy
    # recommendation was ever honored. Both the maintenance and table tools
    # must be invoked here, proving the secondary strategy actually executed
    # a retrieval step, not just that a decision object recorded it.
    chunk_tool = FakeRetrieveChunksTool()
    table_tool = FakeRetrieveTablesTool()
    answer_tool = FakeAnswerQuestionTool()
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=chunk_tool,
            retrieve_tables_tool=table_tool,
        ),
        retrieval_strategy_service=RetrievalStrategyService(),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=RetrievalStrategyPolicy(enabled=True),
        strategy_retry_policy=FakeMultiStrategyRetryPolicy(),
    )

    state = build_agent_state(
        user_input="What are the maintenance intervals?",
        document_id="doc-42",
        selected_document_id="doc-42",
        allow_answer_generation=True,
        include_context=True,
        retrieval_strategy_enabled=True,
    )
    state["question"] = "What are the maintenance intervals?"
    state["route"] = "answer_question"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {"route": "retrieval_qa", "answer_text": "Generic answer."},
        }
    }
    state["reflection_result"] = {
        "decision": {"decision": "RETRIEVE_AGAIN", "reason": "insufficient evidence"},
    }
    state["retry_query"] = "maintenance intervals table"
    state["initial_context_chunks"] = []

    patch = node(state)

    assert table_tool.requests
    assert chunk_tool.requests
    decision = patch["retrieval_strategy_decision"]
    assert decision["primary_strategy"] == "MAINTENANCE_LOOKUP"
    assert "TABLE_LOOKUP" in decision["secondary_strategies"]
