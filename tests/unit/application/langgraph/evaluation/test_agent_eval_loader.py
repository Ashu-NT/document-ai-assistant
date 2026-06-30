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
      deep_research_enabled: true
      llm_research_planning_enabled: false
      retrieval_strategy_enabled: true
      requested_retrieval_strategy: table
      show_retrieval_strategy: true
      show_research_plan: true
      show_research_trace: true
  expected:
    final_route: list_documents
    success: true
    retrieval_strategy_primary: TABLE_LOOKUP
    retrieval_strategy_trace_required: true
    research_plan_required: true
    research_report_required: false
    research_citation_required: false
    research_task_success_min_rate: 0.5
""".strip(),
        encoding="utf-8",
    )

    cases = AgentEvalLoader().load(path)

    assert len(cases) == 1
    assert cases[0].case_id == "AG-001"
    assert cases[0].inputs[0].user_input == "list documents"
    assert cases[0].inputs[0].deep_research_enabled is True
    assert cases[0].inputs[0].show_research_plan is True
    assert cases[0].inputs[0].retrieval_strategy_enabled is True
    assert cases[0].inputs[0].requested_retrieval_strategy == "table"
    assert cases[0].expected.final_route == "list_documents"
    assert cases[0].expected.retrieval_strategy_primary == "TABLE_LOOKUP"
    assert cases[0].expected.research_plan_required is True
    assert cases[0].expected.research_task_success_min_rate == 0.5


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
