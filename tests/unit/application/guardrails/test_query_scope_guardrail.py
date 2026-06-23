import pytest

from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.policies.enterprise_guardrail_policy import (
    EnterpriseGuardrailPolicy,
)
from src.application.guardrails.retrieval.query_scope_guardrail import QueryScopeGuardrail


def make_context(query_text: str) -> GuardrailContext:
    return GuardrailContext(query_text=query_text)


def test_unrelated_query_returns_out_of_scope() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("What is the weather like today?")

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.OUT_OF_SCOPE
    assert result.safe_user_message is not None
    assert len(result.violations) == 1


def test_off_topic_sports_query_returns_out_of_scope() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("Who won the football match yesterday?")

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.OUT_OF_SCOPE


def test_document_query_returns_allow() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("When should the hydraulic filter be replaced?")

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_maintenance_procedure_query_returns_allow() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("How do I install the pressure relief valve?")

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_specification_query_returns_allow() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("What is the maximum operating pressure for pump HP-500?")

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_ambiguous_single_word_query_returns_needs_clarification() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("what?")

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.NEEDS_CLARIFICATION


def test_ambiguous_vague_query_returns_needs_clarification() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("tell me about it")

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.NEEDS_CLARIFICATION


def test_empty_query_returns_needs_clarification() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("")

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.NEEDS_CLARIFICATION


def test_scope_check_disabled_allows_off_topic_query() -> None:
    policy = EnterpriseGuardrailPolicy(block_out_of_scope_queries=False)
    guardrail = QueryScopeGuardrail(policy=policy)
    context = make_context("What is the weather forecast?")

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_part_number_query_returns_allow() -> None:
    guardrail = QueryScopeGuardrail()
    context = make_context("What does part number HP-001 refer to?")

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW
