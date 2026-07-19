import pytest

from src.application.langgraph.reflection.models import ReflectionDecisionType
from src.application.langgraph.reflection.services import ReflectionJsonParser
from src.shared.exceptions import SchemaValidationError


def test_reflection_json_parser_strips_code_fences() -> None:
    parser = ReflectionJsonParser()

    decision = parser.parse(
        """```json
{"decision":"accept","confidence":0.9,"reason":"Looks grounded.","retry_query":null,"clarification_question":null,"missing_information":[]}
```"""
    )

    assert decision.decision == ReflectionDecisionType.ACCEPT
    assert decision.confidence == 0.9


def test_reflection_json_parser_rejects_invalid_json() -> None:
    parser = ReflectionJsonParser()

    with pytest.raises(SchemaValidationError):
        parser.parse("not valid json")


def test_reflection_json_parser_accepts_accept_with_limitations() -> None:
    parser = ReflectionJsonParser()

    decision = parser.parse(
        '{"decision":"ACCEPT_WITH_LIMITATIONS","confidence":0.8,"reason":"Grounded but partial.","retry_query":null,"clarification_question":null,"missing_information":["annual interval"]}'
    )

    assert decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert decision.missing_information == ["annual interval"]


def test_reflection_json_parser_populates_hard_grounding_violation_when_flagged() -> None:
    # Regression guard: an LLM-sourced decision previously had no way to
    # populate diagnostics["hard_grounding_violation"] at all, so
    # ReflectionValidator's downgrade gates (`not hard_grounding_violation`)
    # were unconditionally true for every real LLM decision.
    parser = ReflectionJsonParser()

    decision = parser.parse(
        '{"decision":"CLARIFY","confidence":0.7,"reason":"Answer contradicts evidence.",'
        '"retry_query":null,"clarification_question":"Which interval do you mean?",'
        '"missing_information":[],"grounding_violation":true}'
    )

    assert decision.diagnostics.get("hard_grounding_violation")


def test_reflection_json_parser_omits_hard_grounding_violation_when_not_flagged() -> None:
    parser = ReflectionJsonParser()

    decision = parser.parse(
        '{"decision":"ACCEPT","confidence":0.9,"reason":"Grounded.","retry_query":null,'
        '"clarification_question":null,"missing_information":[],"grounding_violation":false}'
    )

    assert not decision.diagnostics.get("hard_grounding_violation")


def test_reflection_json_parser_defaults_grounding_violation_to_false_when_omitted() -> None:
    parser = ReflectionJsonParser()

    decision = parser.parse(
        '{"decision":"ACCEPT","confidence":0.9,"reason":"Grounded.","retry_query":null,'
        '"clarification_question":null,"missing_information":[]}'
    )

    assert not decision.diagnostics.get("hard_grounding_violation")


def test_reflection_json_parser_populates_entailment_score_and_unsupported_claims() -> None:
    parser = ReflectionJsonParser()

    decision = parser.parse(
        '{"decision":"ACCEPT_WITH_LIMITATIONS","confidence":0.7,'
        '"reason":"Partially unsupported.","retry_query":null,'
        '"clarification_question":null,"missing_information":[],'
        '"entailment_score":0.5,"unsupported_claims":["The tank capacity is 2000 L."]}'
    )

    assert decision.diagnostics["entailment_score"] == 0.5
    assert decision.diagnostics["unsupported_claims"] == [
        "The tank capacity is 2000 L."
    ]


def test_reflection_json_parser_defaults_entailment_score_to_one_when_omitted() -> None:
    parser = ReflectionJsonParser()

    decision = parser.parse(
        '{"decision":"ACCEPT","confidence":0.9,"reason":"Grounded.","retry_query":null,'
        '"clarification_question":null,"missing_information":[]}'
    )

    assert decision.diagnostics["entailment_score"] == 1.0
    assert decision.diagnostics["unsupported_claims"] == []


def test_reflection_json_parser_rejects_entailment_score_out_of_range() -> None:
    parser = ReflectionJsonParser()

    with pytest.raises(SchemaValidationError):
        parser.parse(
            '{"decision":"ACCEPT","confidence":0.9,"reason":"Grounded.","retry_query":null,'
            '"clarification_question":null,"missing_information":[],"entailment_score":1.5}'
        )
