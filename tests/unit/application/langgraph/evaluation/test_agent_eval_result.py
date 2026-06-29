from src.application.langgraph.evaluation import (
    AgentCaseResult,
    AgentEvalReport,
    AgentEvalSummary,
)


def test_agent_eval_report_exposes_case_count() -> None:
    report = AgentEvalReport(
        case_results=[
            AgentCaseResult(case_id="AG-001", name="One", passed=True),
            AgentCaseResult(case_id="AG-002", name="Two", passed=False),
        ],
        summary=AgentEvalSummary(
            case_count=2,
            passed_count=1,
            failed_count=1,
            route_accuracy=1.0,
            document_selection_accuracy=1.0,
            clarification_accuracy=1.0,
            unsafe_block_rate=1.0,
            plan_validity_rate=1.0,
            document_scope_safety_rate=1.0,
            tool_policy_compliance_rate=1.0,
            answer_expectation_rate=1.0,
        ),
    )

    assert report.case_count == 2
