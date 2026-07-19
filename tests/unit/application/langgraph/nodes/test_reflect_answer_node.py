from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.nodes.node_utils import extract_retrieval_query_intent
from src.application.langgraph.nodes.question_answering.reflect_answer_node import (
    ReflectAnswerNode,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
    ReflectionResult,
)
from src.application.langgraph.state import build_agent_state


def _retrieval_result_payload(detected_intent: str | None) -> dict:
    return {
        "context_chunks": [{"chunk_id": "chunk_1"}],
        "retrieval_result": {
            "query": {"detected_intent": detected_intent},
        },
    }


def test_extract_retrieval_query_intent_reads_the_nested_path() -> None:
    payload = _retrieval_result_payload("maintenance")

    assert extract_retrieval_query_intent(payload) == "maintenance"


def test_extract_retrieval_query_intent_returns_none_for_missing_shape() -> None:
    assert extract_retrieval_query_intent({}) is None
    assert extract_retrieval_query_intent(None) is None
    assert extract_retrieval_query_intent({"retrieval_result": "not-a-dict"}) is None
    assert (
        extract_retrieval_query_intent({"retrieval_result": {"query": "not-a-dict"}})
        is None
    )


class _FakeReflectionService:
    def __init__(self, result: ReflectionResult) -> None:
        self.result = result
        self.calls: list[dict] = []

    def review(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


def _accept_result() -> ReflectionResult:
    decision = ReflectionDecision(
        decision=ReflectionDecisionType.ACCEPT,
        confidence=0.9,
        reason="Grounded.",
    )
    return ReflectionResult(
        decision=decision,
        answer_quality_score=1.0,
        evidence_quality_score=1.0,
        grounding_score=1.0,
        document_scope_score=1.0,
        overall_score=1.0,
        accepted=True,
        requires_retry=False,
        requires_clarification=False,
        failed=False,
    )


def test_reflect_answer_node_passes_the_retrieval_query_intent_to_the_service() -> None:
    reflection_service = _FakeReflectionService(_accept_result())
    node = ReflectAnswerNode(
        ToolRegistry(),
        reflection_service=reflection_service,
    )
    state = build_agent_state(
        user_input="What are the maintenance intervals?",
        document_id="doc_1",
        reflection_enabled=True,
    )
    state["question"] = "What are the maintenance intervals?"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "Weekly maintenance every 100 hours.",
                "approved_chunk_ids": ["chunk_1"],
                "rejected_chunk_ids": [],
                "retrieval_result": _retrieval_result_payload("maintenance"),
            },
        }
    }

    node(state)

    assert reflection_service.calls
    assert reflection_service.calls[0]["retrieval_query_intent"] == "maintenance"


def test_reflect_answer_node_passes_none_when_intent_is_unavailable() -> None:
    reflection_service = _FakeReflectionService(_accept_result())
    node = ReflectAnswerNode(
        ToolRegistry(),
        reflection_service=reflection_service,
    )
    state = build_agent_state(
        user_input="What is the operating pressure?",
        document_id="doc_1",
        reflection_enabled=True,
    )
    state["question"] = "What is the operating pressure?"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "6 bar.",
                "approved_chunk_ids": [],
                "rejected_chunk_ids": [],
                "retrieval_result": {},
            },
        }
    }

    node(state)

    assert reflection_service.calls
    assert reflection_service.calls[0]["retrieval_query_intent"] is None


def _clarify_result(
    question: str,
    *,
    diagnostics: dict | None = None,
    missing_information: list[str] | None = None,
) -> ReflectionResult:
    decision = ReflectionDecision(
        decision=ReflectionDecisionType.CLARIFY,
        confidence=0.6,
        reason="Ambiguous request.",
        clarification_question=question,
        missing_information=missing_information or [],
        diagnostics=diagnostics or {},
    )
    return ReflectionResult(
        decision=decision,
        answer_quality_score=0.5,
        evidence_quality_score=0.5,
        grounding_score=0.5,
        document_scope_score=1.0,
        overall_score=0.5,
        accepted=False,
        requires_retry=False,
        requires_clarification=True,
        failed=False,
    )


def test_reflect_answer_node_uses_the_maintenance_clarification_options_end_to_end() -> None:
    # Proves the real (not faked) ClarificationBuilder -> registry wiring:
    # a maintenance-intent CLARIFY decision must surface the migrated
    # maintenance-specific options, not the generic fallback.
    reflection_service = _FakeReflectionService(
        _clarify_result("Do you mean daily or weekly maintenance?")
    )
    node = ReflectAnswerNode(ToolRegistry(), reflection_service=reflection_service)
    state = build_agent_state(
        user_input="What is the maintenance schedule?",
        document_id="doc_1",
        reflection_enabled=True,
    )
    state["question"] = "What is the maintenance schedule?"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "",
                "approved_chunk_ids": [],
                "rejected_chunk_ids": [],
                "retrieval_result": _retrieval_result_payload("maintenance"),
            },
        }
    }

    patch = node(state)

    assert patch["clarification_options"] == [
        {"label": "maintenance tasks", "value": "maintenance tasks"},
        {"label": "maintenance intervals", "value": "maintenance intervals"},
        {"label": "maintenance procedures", "value": "maintenance procedures"},
    ]


def test_reflect_answer_node_uses_ambiguity_options_instead_of_domain_dispatch() -> None:
    # An ambiguity-driven CLARIFY (diagnostics["validator"] ==
    # "ambiguous_intent_clarify") happens to carry a "maintenance"-detected
    # retrieval_query_intent here, but the surfaced options must be the
    # ambiguity's own two labels -- NOT the maintenance-specific fixed
    # options a plain maintenance CLARIFY would get (see the test above).
    reflection_service = _FakeReflectionService(
        _clarify_result(
            "Are you asking about maintenance or troubleshooting?",
            diagnostics={"validator": "ambiguous_intent_clarify"},
            missing_information=["maintenance", "troubleshooting"],
        )
    )
    node = ReflectAnswerNode(ToolRegistry(), reflection_service=reflection_service)
    state = build_agent_state(
        user_input="Show me the maintenance table",
        document_id="doc_1",
        reflection_enabled=True,
    )
    state["question"] = "Show me the maintenance table"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "",
                "approved_chunk_ids": [],
                "rejected_chunk_ids": [],
                "retrieval_result": _retrieval_result_payload("maintenance"),
            },
        }
    }

    patch = node(state)

    assert patch["clarification_options"] == [
        {"label": "maintenance", "value": "maintenance"},
        {"label": "troubleshooting", "value": "troubleshooting"},
    ]
