from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.langgraph.evaluation.models.agent_eval_result import AgentEvalSummary


class AgentEvalSafetyChecksRenderer:
    def render(self, summary: AgentEvalSummary | None) -> list[str]:
        lines = ["", "## Safety Checks", ""]
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
        return lines
