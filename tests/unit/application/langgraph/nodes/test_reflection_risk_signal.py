from src.application.langgraph.nodes.reflection_risk_signal import (
    compute_reflection_risk_signal,
)


def _payload(diagnostics: dict) -> dict:
    return {"diagnostics": diagnostics}


def test_requires_reflection_is_false_when_a_deterministic_renderer_fired() -> None:
    """A deterministic-rendered answer only ever formats already-verified
    structured facts -- no risk signal should be able to override this."""
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": False, "renderer_used": "x"},
                "answer_intent": "safety_warnings",
            }
        )
    )

    assert signal.is_llm_generated is False
    assert signal.requires_reflection is False


def test_requires_reflection_is_false_for_a_plain_llm_answer_with_no_risk_signal() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "answer_intent": "general",
                "coverage_requirement": "best_effort_summary",
            }
        )
    )

    assert signal.is_llm_generated is True
    assert signal.requires_reflection is False


def test_requires_reflection_is_true_for_a_contested_intent() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "deterministic_dispatch_bypass_reason": "contested_intent",
            }
        )
    )

    assert signal.is_contested_intent is True
    assert signal.requires_reflection is True


def test_requires_reflection_is_true_for_a_compound_question() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "deterministic_dispatch_bypass_reason": "compound_question",
            }
        )
    )

    assert signal.is_compound_question is True
    assert signal.requires_reflection is True


def test_requires_reflection_is_true_for_truncated_evidence() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "prompt_payload_truncated": True,
            }
        )
    )

    assert signal.is_evidence_truncated is True
    assert signal.requires_reflection is True


def test_requires_reflection_is_true_for_truncated_raw_appendix() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "raw_source_appendix_truncation": {"truncated": True},
            }
        )
    )

    assert signal.is_evidence_truncated is True
    assert signal.requires_reflection is True


def test_requires_reflection_is_true_for_conflicting_evidence() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "evidence_conflicts": [{"is_critical": True}],
            }
        )
    )

    assert signal.is_evidence_conflicting is True
    assert signal.requires_reflection is True


def test_requires_reflection_is_false_for_a_non_critical_conflict() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "evidence_conflicts": [{"is_critical": False}],
            }
        )
    )

    assert signal.is_evidence_conflicting is False
    assert signal.requires_reflection is False


def test_requires_reflection_is_true_for_exhaustive_list_coverage() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "coverage_requirement": "exhaustive_list",
            }
        )
    )

    assert signal.is_high_stakes_coverage is True
    assert signal.requires_reflection is True


def test_requires_reflection_is_true_for_ordered_procedure_coverage() -> None:
    signal = compute_reflection_risk_signal(
        _payload(
            {
                "decision_trace": {"llm_used": True},
                "coverage_requirement": "ordered_procedure",
            }
        )
    )

    assert signal.is_high_stakes_coverage is True
    assert signal.requires_reflection is True


def test_requires_reflection_is_true_for_each_high_stakes_intent() -> None:
    for intent in (
        "safety_warnings",
        "procedure_steps",
        "troubleshooting",
        "certification_summary",
        "maintenance_summary",
    ):
        signal = compute_reflection_risk_signal(
            _payload({"decision_trace": {"llm_used": True}, "answer_intent": intent})
        )
        assert signal.is_high_stakes_intent is True, intent
        assert signal.requires_reflection is True, intent


def test_requires_reflection_is_false_for_a_routine_intent() -> None:
    for intent in ("general", "specification_summary", "identifier_lookup", "table_summary", "document_summary"):
        signal = compute_reflection_risk_signal(
            _payload({"decision_trace": {"llm_used": True}, "answer_intent": intent})
        )
        assert signal.is_high_stakes_intent is False, intent
        assert signal.requires_reflection is False, intent


def test_handles_missing_or_malformed_payload() -> None:
    assert compute_reflection_risk_signal({}).requires_reflection is False
    assert compute_reflection_risk_signal(None).requires_reflection is False
    assert compute_reflection_risk_signal({"diagnostics": "not-a-dict"}).requires_reflection is False
