from src.application.langgraph.evaluation import (
    AgentCaseResult,
    AgentEvalReport,
    AgentEvalSummary,
    AgentQualityGate,
)


def test_agent_quality_gate_passes_when_metrics_are_high() -> None:
    report = AgentEvalReport(
        summary=AgentEvalSummary(
            case_count=2,
            passed_count=2,
            failed_count=0,
            route_accuracy=1.0,
            document_selection_accuracy=1.0,
            clarification_accuracy=1.0,
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
        )
    )

    result = AgentQualityGate().check(report)

    assert result.passed is True
    assert result.violations == []


def test_agent_quality_gate_fails_when_unsafe_block_rate_is_low() -> None:
    report = AgentEvalReport(
        case_results=[
            AgentCaseResult(
                case_id="AG-002",
                name="Unsafe case",
                passed=False,
                metrics={
                    "unsafe_block_rate": 0.0,
                    "document_scope_safety_rate": 0.0,
                },
            )
        ],
        summary=AgentEvalSummary(
            case_count=2,
            passed_count=1,
            failed_count=1,
            route_accuracy=1.0,
            document_selection_accuracy=1.0,
            clarification_accuracy=1.0,
            unsafe_block_rate=0.5,
            plan_validity_rate=1.0,
            document_scope_safety_rate=0.5,
            tool_policy_compliance_rate=1.0,
            answer_expectation_rate=1.0,
            retrieval_strategy_selection_rate=1.0,
            retrieval_strategy_validity_rate=1.0,
            strategy_fallback_rate=0.0,
            multi_strategy_success_rate=1.0,
            strategy_document_scope_safety_rate=0.5,
            strategy_trace_coverage_rate=1.0,
        )
    )

    result = AgentQualityGate().check(report)

    assert result.passed is False
    assert {violation.metric for violation in result.violations} >= {
        "unsafe_block_rate",
        "document_scope_safety_rate",
    }


def test_agent_quality_gate_ignores_non_applicable_metrics() -> None:
    report = AgentEvalReport(
        case_results=[],
        summary=AgentEvalSummary(
            case_count=1,
            passed_count=1,
            failed_count=0,
            route_accuracy=1.0,
            document_selection_accuracy=0.0,
            clarification_accuracy=0.0,
            unsafe_block_rate=0.0,
            plan_validity_rate=0.0,
            document_scope_safety_rate=0.0,
            tool_policy_compliance_rate=1.0,
            answer_expectation_rate=0.0,
            retrieval_strategy_selection_rate=0.0,
            retrieval_strategy_validity_rate=0.0,
            strategy_fallback_rate=0.0,
            multi_strategy_success_rate=0.0,
            strategy_document_scope_safety_rate=0.0,
            strategy_trace_coverage_rate=0.0,
        ),
    )
    report.case_results.append(
        AgentCaseResult(
            case_id="AG-001",
            name="List documents",
            passed=True,
            metrics={
                "route_accuracy": 1.0,
                "tool_policy_compliance_rate": 1.0,
            },
        )
    )

    result = AgentQualityGate().check(report)

    assert result.passed is True
    assert set(result.checked_metrics) == {
        "route_accuracy",
        "tool_policy_compliance_rate",
    }


def test_agent_quality_gate_checks_research_metrics_when_present() -> None:
    report = AgentEvalReport(
        case_results=[
            AgentCaseResult(
                case_id="AG-003",
                name="Research case",
                passed=False,
                metrics={
                    "deep_research_route_accuracy": 1.0,
                    "research_plan_validity_rate": 0.0,
                    "research_task_success_rate": 0.5,
                },
            )
        ],
        summary=AgentEvalSummary(
            case_count=1,
            passed_count=0,
            failed_count=1,
            route_accuracy=1.0,
            document_selection_accuracy=1.0,
            clarification_accuracy=1.0,
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
            deep_research_route_accuracy=1.0,
            research_plan_validity_rate=0.0,
            research_task_success_rate=0.5,
            research_gap_detection_rate=0.0,
            research_document_scope_safety_rate=0.0,
            research_report_completeness_rate=0.0,
            research_citation_coverage_rate=0.0,
        ),
    )

    result = AgentQualityGate().check(report)

    assert result.passed is False
    assert {violation.metric for violation in result.violations} >= {
        "research_plan_validity_rate",
        "research_task_success_rate",
    }
