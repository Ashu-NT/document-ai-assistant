import json

import pytest

from src.application.langgraph.evaluation import AgentEvalLoader
from src.shared.exceptions import SchemaValidationError


def test_agent_eval_loader_loads_yaml_cases(tmp_path) -> None:
    path = tmp_path / "cases.yaml"
    path.write_text(
        """
- case_id: AG-001
  name: List docs
  tags: [routing]
  inputs:
    - user_input: list documents
  expected:
    final_route: list_documents
    success: true
""".strip(),
        encoding="utf-8",
    )

    cases = AgentEvalLoader().load(path)

    assert len(cases) == 1
    assert cases[0].case_id == "AG-001"
    assert cases[0].inputs[0].user_input == "list documents"
    assert cases[0].expected.final_route == "list_documents"


def test_agent_eval_loader_loads_json_cases(tmp_path) -> None:
    path = tmp_path / "cases.json"
    path.write_text(
        json.dumps(
            [
                {
                    "case_id": "AG-002",
                    "name": "Help",
                    "inputs": [{"user_input": "help"}],
                    "expected": {"final_route": "help", "success": True},
                }
            ]
        ),
        encoding="utf-8",
    )

    cases = AgentEvalLoader().load(path)

    assert len(cases) == 1
    assert cases[0].case_id == "AG-002"
    assert cases[0].expected.success is True


def test_agent_eval_loader_rejects_duplicate_case_ids(tmp_path) -> None:
    path = tmp_path / "cases.yaml"
    path.write_text(
        """
- case_id: AG-001
  name: Case A
  inputs:
    - user_input: list documents
  expected: {}
- case_id: AG-001
  name: Case B
  inputs:
    - user_input: help
  expected: {}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(SchemaValidationError):
        AgentEvalLoader().load(path)


def test_agent_eval_loader_rejects_empty_inputs(tmp_path) -> None:
    path = tmp_path / "cases.yaml"
    path.write_text(
        """
- case_id: AG-003
  name: Empty inputs
  inputs: []
  expected: {}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(SchemaValidationError):
        AgentEvalLoader().load(path)
