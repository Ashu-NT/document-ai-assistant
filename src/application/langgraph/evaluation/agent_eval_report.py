from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.evaluation.agent_eval_result import (
    AgentCaseResult,
    AgentEvalReport,
)


class AgentEvalReportWriter:
    def write_json(
        self,
        report: AgentEvalReport,
        output_path: Path | str,
        *,
        quality_gate_result: Any | None = None,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            json.dumps(
                self.serialize(report, quality_gate_result=quality_gate_result),
                indent=2,
            ),
            encoding="utf-8",
        )
        return resolved_path

    def write_markdown(
        self,
        report: AgentEvalReport,
        output_path: Path | str,
        *,
        quality_gate_result: Any | None = None,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            self.render_markdown(report, quality_gate_result=quality_gate_result),
            encoding="utf-8",
        )
        return resolved_path

    def serialize(
        self,
        report: AgentEvalReport,
        *,
        quality_gate_result: Any | None = None,
    ) -> dict[str, Any]:
        payload = {
            "generated_at": report.generated_at,
            "source_path": report.source_path,
            "filters": report.filters,
            "summary": asdict(report.summary) if report.summary is not None else None,
            "cases": [asdict(case_result) for case_result in report.case_results],
        }
        if quality_gate_result is not None:
            payload["threshold_result"] = serialize_graph_value(
                asdict(quality_gate_result)
            )
        return serialize_graph_value(payload)

    def render_markdown(
        self,
        report: AgentEvalReport,
        *,
        quality_gate_result: Any | None = None,
    ) -> str:
        summary = report.summary
        lines = ["# Agent Evaluation Report", ""]
        if report.source_path:
            lines.extend([f"Source: `{report.source_path}`", ""])

        lines.extend(
            [
                "## Summary",
                "",
                "| Metric | Value |",
                "|---|---:|",
            ]
        )
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

        lines.extend(["", "## Threshold Result", ""])
        if quality_gate_result is None:
            lines.append("Not evaluated.")
        elif getattr(quality_gate_result, "passed", False):
            lines.append("PASS")
        else:
            lines.append("FAIL")
            violations = getattr(quality_gate_result, "violations", [])
            if violations:
                lines.append("")
                for violation in violations:
                    actual = getattr(violation, "actual", None)
                    actual_text = (
                        f"{float(actual):.3f}" if isinstance(actual, int | float) else "n/a"
                    )
                    lines.append(
                        (
                            f"- {violation.metric}: {actual_text} < "
                            f"{violation.threshold:.3f}"
                        )
                    )

        failed_cases = [case for case in report.case_results if not case.passed]
        lines.extend(["", "## Failed Cases", ""])
        if not failed_cases:
            lines.append("No failed cases.")
        else:
            lines.extend(
                [
                    "| Case | Name | Failed Checks |",
                    "|---|---|---|",
                ]
            )
            for case_result in failed_cases:
                lines.append(
                    (
                        f"| {case_result.case_id} | {case_result.name} | "
                        f"{', '.join(case_result.failed_checks)} |"
                    )
                )

        lines.extend(["", "## Cases", ""])
        for case_result in report.case_results:
            lines.extend(self._render_case(case_result))

        lines.extend(["", "## Safety Checks", ""])
        lines.append(
            (
                f"- unsafe blocked: {summary.unsafe_block_rate:.3f}"
                if summary is not None
                else "- unsafe blocked: n/a"
            )
        )
        lines.append(
            (
                f"- out-of-scope redirect: {summary.out_of_scope_redirect_rate:.3f}"
                if summary is not None
                else "- out-of-scope redirect: n/a"
            )
        )
        lines.append(
            (
                f"- prompt injection blocked: {summary.prompt_injection_block_rate:.3f}"
                if summary is not None
                else "- prompt injection blocked: n/a"
            )
        )
        lines.append(
            (
                f"- tool policy compliance: {summary.tool_policy_compliance_rate:.3f}"
                if summary is not None
                else "- tool policy compliance: n/a"
            )
        )
        lines.append(
            (
                f"- document scope safety: {summary.document_scope_safety_rate:.3f}"
                if summary is not None
                else "- document scope safety: n/a"
            )
        )
        lines.append("")
        return "\n".join(lines)

    def _render_case(self, case_result: AgentCaseResult) -> list[str]:
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
                        f"{_preview(turn_result.response_text)}"
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


def _preview(value: str | None, limit: int = 180) -> str:
    if not value:
        return "-"
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."
