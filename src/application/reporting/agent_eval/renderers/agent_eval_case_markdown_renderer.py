from __future__ import annotations

from typing import TYPE_CHECKING

from src.shared.text.text_preview import preview_text

if TYPE_CHECKING:
    from src.application.langgraph.evaluation.models.agent_eval_result import AgentCaseResult


class AgentEvalCaseMarkdownRenderer:
    def render(self, case_result: AgentCaseResult) -> list[str]:
        lines = [
            f"### {case_result.case_id} - {case_result.name}",
            f"- Passed: {'yes' if case_result.passed else 'no'}",
            f"- Failed checks: {', '.join(case_result.failed_checks) or '-'}",
        ]
        for index, turn_result in enumerate(case_result.turn_results, start=1):
            lines.extend(
                [
                    f"- Turn {index} route: {turn_result.route or '-'}",
                    (
                        f"- Turn {index} selected document: "
                        f"{turn_result.selected_document_title or '-'} "
                        f"({turn_result.selected_document_id or '-'})"
                    ),
                    (
                        f"- Turn {index} tools: "
                        f"{', '.join(turn_result.tool_names) or '-'}"
                    ),
                    (
                        f"- Turn {index} plan tools: "
                        f"{', '.join(turn_result.plan_tool_names) or '-'}"
                    ),
                    (
                        f"- Turn {index} response excerpt: "
                        f"{preview_text(turn_result.response_text, 180, empty_fallback='-')}"
                    ),
                ]
            )
            if turn_result.retrieval_strategy_primary is not None:
                lines.extend(
                    [
                        (
                            f"- Turn {index} retrieval strategy: "
                            f"{turn_result.retrieval_strategy_primary}"
                        ),
                        (
                            f"- Turn {index} retrieval strategy secondary: "
                            f"{', '.join(turn_result.retrieval_strategy_secondary) or '-'}"
                        ),
                        (
                            f"- Turn {index} retrieval strategy trace present: "
                            f"{'yes' if turn_result.retrieval_strategy_trace_present else 'no'}"
                        ),
                    ]
                )
            if (
                turn_result.research_plan_present
                or turn_result.research_report_present
                or turn_result.research_task_count > 0
            ):
                lines.extend(
                    [
                        (
                            f"- Turn {index} research plan: "
                            f"{'yes' if turn_result.research_plan_present else 'no'} "
                            f"(tasks={turn_result.research_plan_task_count})"
                        ),
                        (
                            f"- Turn {index} research tasks: "
                            f"{turn_result.research_task_success_count}/"
                            f"{turn_result.research_task_count} succeeded"
                        ),
                        (
                            f"- Turn {index} research gaps: "
                            f"{turn_result.research_gap_count}"
                        ),
                        (
                            f"- Turn {index} research report: "
                            f"{'yes' if turn_result.research_report_present else 'no'} "
                            f"(sections={turn_result.research_report_section_count})"
                        ),
                        (
                            f"- Turn {index} research citations: "
                            f"{turn_result.research_citation_count}"
                        ),
                    ]
                )
        lines.append("")
        return lines
