from pathlib import Path
from types import SimpleNamespace

from tests.unit.cli_scripts.test_cli_scripts import _load_script

from src.application.langgraph.evaluation import (
    AgentEvalReport,
    AgentEvalSummary,
    AgentQualityGateResult,
    AgentThresholdViolation,
)


def test_run_agent_eval_module_importable() -> None:
    mod = _load_script("run_agent_eval")

    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_run_agent_eval_parses_arguments() -> None:
    mod = _load_script("run_agent_eval")

    args = mod.parse_args(
        [
            "--case-id",
            "AG-001",
            "--tag",
            "safety",
            "--llm-planning",
            "--retrieval-strategy",
            "table",
            "--llm-retrieval-strategy",
            "--fail-on-threshold",
            "--json",
        ]
    )

    assert args.case_id == ["AG-001"]
    assert args.tag == ["safety"]
    assert args.llm_planning is True
    assert args.retrieval_strategy == "table"
    assert args.llm_retrieval_strategy is True
    assert args.fail_on_threshold is True
    assert args.json is True


def test_run_agent_eval_main_exits_non_zero_when_threshold_fails(
    monkeypatch,
    tmp_path,
) -> None:
    mod = _load_script("run_agent_eval")
    report = AgentEvalReport(
        summary=AgentEvalSummary(
            case_count=1,
            passed_count=0,
            failed_count=1,
            route_accuracy=0.0,
            document_selection_accuracy=0.0,
            clarification_accuracy=0.0,
            unsafe_block_rate=0.0,
            plan_validity_rate=0.0,
            document_scope_safety_rate=0.0,
            tool_policy_compliance_rate=0.0,
            answer_expectation_rate=0.0,
            retrieval_strategy_selection_rate=0.0,
            retrieval_strategy_validity_rate=0.0,
            strategy_fallback_rate=0.0,
            multi_strategy_success_rate=0.0,
            strategy_document_scope_safety_rate=0.0,
            strategy_trace_coverage_rate=0.0,
        )
    )
    gate_result = AgentQualityGateResult(
        passed=False,
        violations=[
            AgentThresholdViolation(
                metric="unsafe_block_rate",
                actual=0.0,
                threshold=1.0,
                message="unsafe block too low",
            )
        ],
        checked_metrics={"unsafe_block_rate": 0.0},
    )
    fake_runtime = SimpleNamespace(
        graph_runtime=None,
        report_writer=SimpleNamespace(
            serialize=lambda *_args, **_kwargs: {"summary": {"case_count": 1}}
        ),
    )

    def fake_run_agent_eval(**_kwargs):
        return fake_runtime, (
            report,
            gate_result,
            tmp_path / "agent_eval_report.json",
            tmp_path / "agent_eval_report.md",
        )

    monkeypatch.setattr(mod, "run_agent_eval", fake_run_agent_eval)
    monkeypatch.setattr(mod.agent_cli, "close_runtime", lambda _runtime: None)

    exit_code = mod.main(["--fail-on-threshold"])

    assert exit_code == 2
