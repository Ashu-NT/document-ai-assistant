from src.application.guardrails.policies.answer_guardrail_policy import AnswerGuardrailPolicy
from src.application.guardrails.policies.enterprise_guardrail_policy import EnterpriseGuardrailPolicy
from src.application.guardrails.policies.retrieval_guardrail_policy import RetrievalGuardrailPolicy
from src.application.guardrails.policies.safety_guardrail_policy import SafetyGuardrailPolicy


def test_retrieval_guardrail_policy_has_sensible_defaults() -> None:
    policy = RetrievalGuardrailPolicy()

    assert 0.0 < policy.min_retrieval_score < 1.0
    assert policy.min_evidence_chunks >= 1
    assert policy.identifier_evidence_required is True
    assert policy.min_safety_evidence_chunks >= 1


def test_retrieval_guardrail_policy_is_configurable() -> None:
    policy = RetrievalGuardrailPolicy(
        min_retrieval_score=0.75,
        min_evidence_chunks=3,
        identifier_evidence_required=False,
    )

    assert policy.min_retrieval_score == 0.75
    assert policy.min_evidence_chunks == 3
    assert policy.identifier_evidence_required is False


def test_enterprise_guardrail_policy_has_sensible_defaults() -> None:
    policy = EnterpriseGuardrailPolicy()

    assert policy.block_out_of_scope_queries is True
    assert policy.require_citations is True
    assert policy.max_context_tokens > 0


def test_enterprise_guardrail_policy_is_configurable() -> None:
    policy = EnterpriseGuardrailPolicy(
        block_out_of_scope_queries=False,
        require_citations=False,
        max_context_tokens=8000,
    )

    assert policy.block_out_of_scope_queries is False
    assert policy.require_citations is False
    assert policy.max_context_tokens == 8000


def test_safety_guardrail_policy_has_sensible_defaults() -> None:
    policy = SafetyGuardrailPolicy()

    assert policy.block_ungrounded_safety_answers is True
    assert policy.min_safety_evidence_chunks >= 1
    assert policy.require_safety_source_citation is True


def test_safety_guardrail_policy_is_configurable() -> None:
    policy = SafetyGuardrailPolicy(
        block_ungrounded_safety_answers=False,
        min_safety_evidence_chunks=2,
        require_safety_source_citation=False,
    )

    assert policy.block_ungrounded_safety_answers is False
    assert policy.min_safety_evidence_chunks == 2


def test_answer_guardrail_policy_has_sensible_defaults() -> None:
    policy = AnswerGuardrailPolicy()

    assert policy.require_citations is True
    assert policy.block_unsupported_claims is True
    assert policy.block_unsupported_suggestions is True
    assert 0.0 < policy.min_claim_support_score < 1.0


def test_answer_guardrail_policy_is_configurable() -> None:
    policy = AnswerGuardrailPolicy(
        require_citations=False,
        min_claim_support_score=0.80,
    )

    assert policy.require_citations is False
    assert policy.min_claim_support_score == 0.80


def test_policies_are_frozen_dataclasses() -> None:
    policy = RetrievalGuardrailPolicy()

    try:
        policy.min_retrieval_score = 0.99  # type: ignore[misc]
        assert False, "Expected FrozenInstanceError"
    except Exception:
        pass
