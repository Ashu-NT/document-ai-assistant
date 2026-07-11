from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.application.reporting.agent_eval.renderers.agent_eval_case_markdown_renderer import (
    AgentEvalCaseMarkdownRenderer,
)
from src.application.reporting.agent_eval.renderers.agent_eval_safety_checks_renderer import (
    AgentEvalSafetyChecksRenderer,
)
from src.application.reporting.agent_eval.renderers.agent_eval_summary_table_renderer import (
    AgentEvalSummaryTableRenderer,
)
from src.application.reporting.agent_eval.renderers.agent_eval_threshold_result_renderer import (
    AgentEvalThresholdResultRenderer,
)

if TYPE_CHECKING:
    from src.application.langgraph.evaluation.agent_eval_result import (
        AgentEvalReport,
    )


class AgentEvalReportMarkdownRenderer:
    def __init__(
        self,
        *,
        summary_table_renderer: AgentEvalSummaryTableRenderer | None = None,
        threshold_result_renderer: AgentEvalThresholdResultRenderer | None = None,
        case_renderer: AgentEvalCaseMarkdownRenderer | None = None,
        safety_checks_renderer: AgentEvalSafetyChecksRenderer | None = None,
    ) -> None:
        self.summary_table_renderer = (
            summary_table_renderer or AgentEvalSummaryTableRenderer()
        )
        self.threshold_result_renderer = (
            threshold_result_renderer or AgentEvalThresholdResultRenderer()
        )
        self.case_renderer = case_renderer or AgentEvalCaseMarkdownRenderer()
        self.safety_checks_renderer = (
            safety_checks_renderer or AgentEvalSafetyChecksRenderer()
        )

    def render(
        self,
        report: AgentEvalReport,
        *,
        quality_gate_result: Any | None = None,
    ) -> str:
        summary = report.summary
        lines = ["# Agent Evaluation Report", ""]
        if report.source_path:
            lines.extend([f"Source: `{report.source_path}`", ""])

        lines.extend(self.summary_table_renderer.render(summary))
        lines.extend(self.threshold_result_renderer.render(quality_gate_result))

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
            lines.extend(self.case_renderer.render(case_result))

        lines.extend(self.safety_checks_renderer.render(summary))
        return "\n".join(lines)
