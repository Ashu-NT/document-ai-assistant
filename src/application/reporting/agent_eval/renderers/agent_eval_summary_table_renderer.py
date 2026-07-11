from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.langgraph.evaluation.agent_eval_result import AgentEvalSummary


class AgentEvalSummaryTableRenderer:
    def render(self, summary: AgentEvalSummary | None) -> list[str]:
        lines = [
            "## Summary",
            "",
            "| Metric | Value |",
            "|---|---:|",
        ]
        if summary is not None:
            lines.extend(
                [
                    f"| case_count | {summary.case_count} |",
                    f"| passed_count | {summary.passed_count} |",
                    f"| failed_count | {summary.failed_count} |",
                    f"| route_accuracy | {summary.route_accuracy:.3f} |",
                    (
                        "| deep_research_route_accuracy | "
                        f"{summary.deep_research_route_accuracy:.3f} |"
                    ),
                    (
                        "| document_selection_accuracy | "
                        f"{summary.document_selection_accuracy:.3f} |"
                    ),
                    f"| clarification_accuracy | {summary.clarification_accuracy:.3f} |",
                    f"| unsafe_block_rate | {summary.unsafe_block_rate:.3f} |",
                    f"| guardrail_block_rate | {summary.guardrail_block_rate:.3f} |",
                    (
                        "| out_of_scope_redirect_rate | "
                        f"{summary.out_of_scope_redirect_rate:.3f} |"
                    ),
                    (
                        "| false_positive_guardrail_rate | "
                        f"{summary.false_positive_guardrail_rate:.3f} |"
                    ),
                    (
                        "| false_negative_guardrail_rate | "
                        f"{summary.false_negative_guardrail_rate:.3f} |"
                    ),
                    (
                        "| prompt_injection_block_rate | "
                        f"{summary.prompt_injection_block_rate:.3f} |"
                    ),
                    (
                        "| destructive_tool_block_rate | "
                        f"{summary.destructive_tool_block_rate:.3f} |"
                    ),
                    (
                        "| grounding_failure_catch_rate | "
                        f"{summary.grounding_failure_catch_rate:.3f} |"
                    ),
                    f"| plan_validity_rate | {summary.plan_validity_rate:.3f} |",
                    (
                        "| document_scope_safety_rate | "
                        f"{summary.document_scope_safety_rate:.3f} |"
                    ),
                    (
                        "| tool_policy_compliance_rate | "
                        f"{summary.tool_policy_compliance_rate:.3f} |"
                    ),
                    (
                        "| answer_expectation_rate | "
                        f"{summary.answer_expectation_rate:.3f} |"
                    ),
                    (
                        "| retrieval_strategy_selection_rate | "
                        f"{summary.retrieval_strategy_selection_rate:.3f} |"
                    ),
                    (
                        "| retrieval_strategy_validity_rate | "
                        f"{summary.retrieval_strategy_validity_rate:.3f} |"
                    ),
                    (
                        "| strategy_fallback_rate | "
                        f"{summary.strategy_fallback_rate:.3f} |"
                    ),
                    (
                        "| multi_strategy_success_rate | "
                        f"{summary.multi_strategy_success_rate:.3f} |"
                    ),
                    (
                        "| strategy_document_scope_safety_rate | "
                        f"{summary.strategy_document_scope_safety_rate:.3f} |"
                    ),
                    (
                        "| strategy_trace_coverage_rate | "
                        f"{summary.strategy_trace_coverage_rate:.3f} |"
                    ),
                    (
                        "| research_plan_validity_rate | "
                        f"{summary.research_plan_validity_rate:.3f} |"
                    ),
                    (
                        "| research_task_success_rate | "
                        f"{summary.research_task_success_rate:.3f} |"
                    ),
                    (
                        "| research_gap_detection_rate | "
                        f"{summary.research_gap_detection_rate:.3f} |"
                    ),
                    (
                        "| research_document_scope_safety_rate | "
                        f"{summary.research_document_scope_safety_rate:.3f} |"
                    ),
                    (
                        "| research_report_completeness_rate | "
                        f"{summary.research_report_completeness_rate:.3f} |"
                    ),
                    (
                        "| research_citation_coverage_rate | "
                        f"{summary.research_citation_coverage_rate:.3f} |"
                    ),
                ]
            )
        return lines
