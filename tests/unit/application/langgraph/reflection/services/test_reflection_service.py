import logging

from src.application.langgraph.nodes.retrieval_intent_decision import (
    RetrievalIntentDecision,
)
from src.application.langgraph.reflection.models import ReflectionDecisionType
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.services import ReflectionService
from src.application.langgraph.reflection.services.query_ambiguity_detector import (
    QueryAmbiguityDetector,
)


class _FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "response_schema": response_schema,
            }
        )
        return self.response


def test_reflection_service_accepts_grounded_answer_without_llm() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="The maintenance interval is 500 hours on page 12.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "content": "Maintenance interval is 500 hours.",
                "source": {"page_start": 12},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_1", "source": {"page_start": 12}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT
    assert result.accepted is True


def test_reflection_service_requests_retry_when_evidence_is_missing() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.FAIL
    assert result.failed is True


def test_reflection_service_rejects_maintenance_interval_answer_with_unrelated_specs() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer=(
            "The maintenance interval is weekly on page 58. Voltage: 400 V. "
            "Installed power: 5.5 kW."
        ),
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_58", "source": {"page_start": 58}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert "technical specifications" in result.decision.reason.lower()
    assert result.decision.retry_query is not None


def test_reflection_service_rejects_maintenance_interval_answer_without_references() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="The maintenance interval is weekly.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert "grounded references" in result.decision.reason.lower()
    assert result.accepted is True


def test_reflection_service_downgrades_clarify_without_question_to_accept_with_limitations() -> None:
    llm_service = _FakeLLMService(
            '{"decision":"CLARIFY","confidence":0.61,"reason":"Need clarification.","retry_query":null,"clarification_question":null,"missing_information":["annual interval"]}'
        )
    service = ReflectionService(
        llm_service=llm_service,
        policy=ReflectionPolicy(enabled=True),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="Weekly maintenance latest after 100 operating hours (page 58).",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_58", "source": {"page_start": 58}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.requires_clarification is False
    assert result.failed is False
    assert isinstance(llm_service.calls[0]["response_schema"], dict)


def test_reflection_service_synthesizes_clarify_for_a_genuinely_ambiguous_question() -> None:
    """End-to-end proof of the ambiguity-driven clarification trigger: a
    question that produces an exact RetrievalQueryIntent scoring tie (table
    vs. troubleshooting -- confirmed via direct classification) must turn a
    CLARIFY-without-question (which would otherwise fail safe, see
    test_reflection_service_downgrades_clarify_without_question_to_accept_with_limitations)
    into a real clarification instead."""
    llm_service = _FakeLLMService(
        '{"decision":"CLARIFY","confidence":0.6,"reason":"Ambiguous.","retry_query":null,'
        '"clarification_question":null,"missing_information":[]}'
    )
    service = ReflectionService(
        llm_service=llm_service,
        policy=ReflectionPolicy(enabled=True),
    )

    result = service.review(
        original_user_question="Show me the fault code table",
        generated_answer="The document lists several fault codes in a table.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent=None,
        approved_chunks=[],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.CLARIFY
    assert (
        result.decision.clarification_question
        == "Are you asking about table or troubleshooting?"
    )
    assert result.requires_clarification is True
    assert result.diagnostics["ambiguous_intent_tie"] == {
        "intent_label": "table",
        "runner_up_label": "troubleshooting",
    }


def test_reflection_service_uses_persisted_retrieval_intent_decision_without_reclassifying() -> None:
    """PR 2/3 (answering_flow_weakness_remediation_plan.md): reflection must
    read the SAME classification that already drove retrieval instead of
    calling RetrievalQueryIntentInferer.classify() a second, independent
    time. Reuses the exact tie scenario from the test above, but supplies
    the persisted decision and asserts the underlying inferer is never
    invoked at all -- the fix for the real duplicate-classification bug."""

    class _ExplodingIntentInferer:
        def classify(self, query):
            raise AssertionError(
                "QueryAmbiguityDetector reclassified instead of using the "
                "persisted retrieval_intent_decision"
            )

    llm_service = _FakeLLMService(
        '{"decision":"CLARIFY","confidence":0.6,"reason":"Ambiguous.","retry_query":null,'
        '"clarification_question":null,"missing_information":[]}'
    )
    service = ReflectionService(
        llm_service=llm_service,
        policy=ReflectionPolicy(enabled=True),
        query_ambiguity_detector=QueryAmbiguityDetector(
            intent_inferer=_ExplodingIntentInferer()
        ),
    )

    result = service.review(
        original_user_question="Show me the fault code table",
        generated_answer="The document lists several fault codes in a table.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent=None,
        approved_chunks=[],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=0,
        retrieval_query_intent="table",
        retrieval_intent_decision=RetrievalIntentDecision(
            intent="table",
            best_score=4,
            runner_up_intent="troubleshooting",
            runner_up_score=4,
            gap=0,
            confidence=0.62,
        ),
    )

    assert result.decision.decision == ReflectionDecisionType.CLARIFY
    assert (
        result.decision.clarification_question
        == "Are you asking about table or troubleshooting?"
    )
    assert result.diagnostics["ambiguous_intent_tie"] == {
        "intent_label": "table",
        "runner_up_label": "troubleshooting",
    }


def test_reflection_service_retries_targeting_a_clause_the_answer_never_addressed() -> None:
    """End-to-end proof of the multi-clause coverage trigger (Phase 4): a
    two-part question whose answer only covers the first part must
    RETRIEVE_AGAIN with a retry_query targeting the missed second part,
    even though the answered part alone is well grounded."""
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question=(
            "What is the operating pressure and what safety warnings apply?"
        ),
        generated_answer="The operating pressure is 6 bar, as shown on page 4.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="specification_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_4",
                "document_id": "doc_1",
                "content": "Operating pressure is 6 bar.",
                "source": {"page_start": 4},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_4", "source": {"page_start": 4}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert result.decision.retry_query == "what safety warnings apply?"
    assert result.diagnostics["clause_coverage"] == {
        "uncovered_clauses": ["what safety warnings apply?"],
        "is_fully_covered": False,
    }


def test_reflection_service_clause_coverage_diagnostics_is_none_for_a_single_clause_question() -> None:
    result = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    ).review(
        original_user_question="What is the pump maximum flow rate specification?",
        generated_answer="The pump maximum flow rate specification is 120 m3/h, as shown on page 4.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="specification_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_4",
                "document_id": "doc_1",
                "content": "Pump maximum flow rate is 120 m3/h.",
                "source": {"page_start": 4},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_4", "source": {"page_start": 4}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.diagnostics["clause_coverage"] is None
    assert result.decision.decision == ReflectionDecisionType.ACCEPT


def test_reflection_service_retry_limit_with_evidence_returns_accept_with_limitations() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False, max_retrieval_retries=1),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="Weekly maintenance latest after 100 operating hours.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=1,
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.accepted is True


def test_reflection_service_spec_only_evidence_stays_retry_or_fail() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="The pump voltage is 400 V and the installed power is 5.5 kW.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_spec",
                "document_id": "doc_1",
                "chunk_type": "technical_specification",
                "content": "Voltage 400 V. Installed power 5.5 kW.",
                "source": {"page_start": 50},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_spec", "source": {"page_start": 50}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision in {
        ReflectionDecisionType.RETRIEVE_AGAIN,
        ReflectionDecisionType.FAIL,
    }


def test_reflection_service_fails_when_answer_cites_unapproved_pages() -> None:
    service = ReflectionService(policy=ReflectionPolicy(enabled=False))

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="The maintenance interval is weekly on page 10.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_10", "source": {"page_start": 10}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.FAIL
    assert "approved evidence" in result.decision.reason.lower()


def _review_kwargs(**overrides: object) -> dict:
    base = dict(
        original_user_question="What is the pump flow rate specification?",
        generated_answer="The pump flow rate is 120 m3/h, as shown on page 4.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="specification",
        approved_chunks=[
            {
                "chunk_id": "chunk_4",
                "document_id": "doc_1",
                "content": "Pump flow rate is 120 m3/h.",
                "source": {"page_start": 4},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_4", "source": {"page_start": 4}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )
    base.update(overrides)
    return base


def test_review_without_reference_notes_is_byte_identical_to_before_the_change() -> None:
    """Mandatory backward-compatibility test at the service level: omitting
    reference_notes (the new, optional review() kwarg) must produce exactly
    the same scores as calling review() with reference_notes=None."""
    service = ReflectionService(policy=ReflectionPolicy(enabled=False))

    without_param = service.review(**_review_kwargs())
    with_explicit_none = service.review(**_review_kwargs(reference_notes=None))

    assert without_param.answer_quality_score == with_explicit_none.answer_quality_score
    assert without_param.evidence_quality_score == with_explicit_none.evidence_quality_score
    assert without_param.overall_score == with_explicit_none.overall_score


def test_review_caps_answer_quality_when_reference_note_is_unresolved() -> None:
    service = ReflectionService(policy=ReflectionPolicy(enabled=False))

    fully_resolved = service.review(
        **_review_kwargs(
            reference_notes=[
                {
                    "note_id": "r1",
                    "claim_text": "Pump flow rate is 120 m3/h.",
                    "source_number": 1,
                    "chunk_id": "chunk_4",
                }
            ]
        )
    )
    unresolved = service.review(
        **_review_kwargs(
            reference_notes=[
                {
                    "note_id": "r1",
                    "claim_text": "Pump flow rate is 120 m3/h.",
                    "source_number": 1,
                    "chunk_id": None,
                }
            ]
        )
    )

    assert unresolved.answer_quality_score <= 0.5
    assert unresolved.answer_quality_score < fully_resolved.answer_quality_score


def test_review_logs_reflection_score_recorded_with_expected_fields(caplog) -> None:
    service = ReflectionService(policy=ReflectionPolicy(enabled=False))

    with caplog.at_level(logging.INFO):
        service.review(**_review_kwargs())

    matching_records = [
        record for record in caplog.records if record.message == "reflection_score_recorded"
    ]
    assert len(matching_records) == 1
    record = matching_records[0]
    assert record.decision == ReflectionDecisionType.ACCEPT.value
    assert isinstance(record.answer_quality_score, float)
    assert isinstance(record.evidence_quality_score, float)
    assert isinstance(record.grounding_score, float)
    assert isinstance(record.overall_score, float)
    assert record.intent == "specification"


def test_review_downgrades_fail_for_a_non_domain_intent_with_good_generic_evidence() -> None:
    # End-to-end proof of the Phase 1 adaptive-reflection registry: a
    # "troubleshooting" retrieval_query_intent has no hardcoded domain
    # detector (unlike maintenance/table/identifier) -- before this
    # feature, a FAIL decision here had no fallback leniency at all.
    # EvidenceSufficiencyStrategyRegistry now falls back to
    # GenericEvidenceSufficiencyStrategy for this intent, and its SUFFICIENT
    # verdict (built from the same generic signals _review_kwargs()'s
    # grounded scenario already satisfies) downgrades the FAIL.
    llm_service = _FakeLLMService(
        '{"decision":"FAIL","confidence":0.6,"reason":"Evidence seemed thin.",'
        '"retry_query":null,"clarification_question":null,"missing_information":[]}'
    )
    service = ReflectionService(
        llm_service=llm_service,
        policy=ReflectionPolicy(enabled=True),
    )

    result = service.review(
        **_review_kwargs(
            answer_intent="troubleshooting",
            retrieval_query_intent="troubleshooting",
        )
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.decision.diagnostics.get("validator") == "fail_downgraded"
    assert (
        result.diagnostics["evidence_sufficiency_verdict"]
        == "SUFFICIENT"
    )
    assert result.diagnostics["retrieval_query_intent"] == "troubleshooting"
