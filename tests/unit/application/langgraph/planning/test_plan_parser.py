from src.application.langgraph.planning import PlanParser


def test_plan_parser_parses_valid_json_plan() -> None:
    result = PlanParser().parse(
        """
        {
          "goal": "Find and answer",
          "reason": "Need document lookup first.",
          "steps": [
            {
              "step_id": "step_1",
              "tool_name": "find_document",
              "description": "Find the document",
              "args": {"query_text": "pump"},
              "output_key": "lookup",
              "depends_on": [],
              "required": true
            }
          ]
        }
        """
    )

    assert result.success is True
    assert result.plan is not None
    assert result.plan.source == "llm"
    assert result.plan.steps[0].source == "llm"


def test_plan_parser_strips_code_fences() -> None:
    result = PlanParser().parse(
        """```json
        {
          "goal": "Find and answer",
          "steps": [
            {
              "step_id": "step_1",
              "tool_name": "find_document",
              "description": "Find the document",
              "args": {"query_text": "pump"},
              "output_key": "lookup",
              "depends_on": [],
              "required": true
            }
          ]
        }
        ```"""
    )

    assert result.success is True
    assert result.plan is not None


def test_plan_parser_rejects_invalid_json() -> None:
    result = PlanParser().parse("not json")

    assert result.success is False
    assert result.error_code == "plan_json_invalid"


def test_plan_parser_rejects_missing_steps() -> None:
    result = PlanParser().parse('{"goal":"Only goal"}')

    assert result.success is False
    assert result.error_code == "plan_steps_missing"
