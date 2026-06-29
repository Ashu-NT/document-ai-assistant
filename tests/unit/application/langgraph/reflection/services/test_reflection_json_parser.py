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
