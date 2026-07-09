from src.application.langgraph.evaluation import (
    AgentCaseResult,
    AgentEvalReport,
    AgentEvalSummary,
    AgentQualityGateResult,
    AgentThresholdViolation,
    AgentTurnResult,
)
from src.application.reporting.agent_eval import AgentEvalReportWriter


def test_agent_eval_report_writer_writes_json_and_markdown(tmp_path) -> None:
    report = AgentEvalReport(
        case_results=[
            AgentCaseResult(
                case_id="AG-001",
                name="List documents",
                passed=False,
                failed_checks=["route_accuracy"],
                turn_results=[
                    AgentTurnResult(
                        user_input="list documents",
                        route="list_documents",
                        success=True,
                        response_text="Found documents.",
                        selected_document_id=None,
                        selected_document_title=None,
                        tool_names=["list_documents"],
                        retrieval_strategy_primary="TABLE_LOOKUP",
                        retrieval_strategy_secondary=["GENERAL_HYBRID"],
                        retrieval_strategy_trace_present=True,
                        research_plan_present=True,
                        research_plan_task_count=2,
                        research_task_count=2,
                        research_task_success_count=2,
                        research_report_present=True,
                        research_report_section_count=1,
                        research_citation_count=1,
                    )
                ],
                metrics={"route_accuracy": 0.0},
            )
        ],
        summary=AgentEvalSummary(
            case_count=1,
            passed_count=0,
            failed_count=1,
            route_accuracy=0.0,
            document_selection_accuracy=0.0,
            clarification_accuracy=0.0,
            unsafe_block_rate=1.0,
            plan_validity_rate=1.0,
            document_scope_safety_rate=1.0,
            tool_policy_compliance_rate=1.0,
            answer_expectation_rate=1.0,
            retrieval_strategy_selection_rate=1.0,
            retrieval_strategy_validity_rate=1.0,
            strategy_fallback_rate=0.0,
            multi_strategy_success_rate=1.0,
            strategy_document_scope_safety_rate=1.0,
            strategy_trace_coverage_rate=1.0,
        ),
        source_path="src/config/evaluation/agent_eval_cases.yaml",
    )
    gate_result = AgentQualityGateResult(
        passed=False,
        violations=[
            AgentThresholdViolation(
                metric="route_accuracy",
                actual=0.0,
                threshold=0.9,
                message="route_accuracy too low",
            )
        ],
        checked_metrics={"route_accuracy": 0.0},
    )
    writer = AgentEvalReportWriter()

    json_path = writer.write_json(
        report,
        tmp_path / "agent_eval_report.json",
        quality_gate_result=gate_result,
    )
    markdown_path = writer.write_markdown(
        report,
        tmp_path / "agent_eval_report.md",
        quality_gate_result=gate_result,
    )

    json_text = json_path.read_text(encoding="utf-8")
    markdown_text = markdown_path.read_text(encoding="utf-8")
    assert '"threshold_result"' in json_text
    assert "# Agent Evaluation Report" in markdown_text
    assert "## Failed Cases" in markdown_text
    assert "AG-001" in markdown_text
    assert "retrieval strategy: TABLE_LOOKUP" in markdown_text
    assert "research plan: yes (tasks=2)" in markdown_text


def test_write_json_and_write_markdown_delegate_to_injected_serializer_and_renderer(
    tmp_path,
) -> None:
    from unittest.mock import MagicMock

    fake_serializer = MagicMock()
    fake_serializer.serialize.return_value = {"ok": True}
    fake_renderer = MagicMock()
    fake_renderer.render.return_value = "# Rendered"

    writer = AgentEvalReportWriter(
        json_serializer=fake_serializer,
        markdown_renderer=fake_renderer,
    )
    report = AgentEvalReport(case_results=[])

    json_path = writer.write_json(report, tmp_path / "r.json")
    markdown_path = writer.write_markdown(report, tmp_path / "r.md")

    fake_serializer.serialize.assert_called_once_with(
        report, quality_gate_result=None
    )
    fake_renderer.render.assert_called_once_with(report, quality_gate_result=None)
    assert json_path.read_text(encoding="utf-8") == '{\n  "ok": true\n}'
    assert markdown_path.read_text(encoding="utf-8") == "# Rendered"
