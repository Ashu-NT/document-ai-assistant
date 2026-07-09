from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.application.reporting.agent_eval.agent_eval_report_json_serializer import (
    AgentEvalReportJsonSerializer,
)
from src.application.reporting.agent_eval.agent_eval_report_markdown_renderer import (
    AgentEvalReportMarkdownRenderer,
)

if TYPE_CHECKING:
    from src.application.langgraph.evaluation.agent_eval_result import AgentEvalReport


class AgentEvalReportWriter:
    def __init__(
        self,
        *,
        json_serializer: AgentEvalReportJsonSerializer | None = None,
        markdown_renderer: AgentEvalReportMarkdownRenderer | None = None,
    ) -> None:
        self.json_serializer = json_serializer or AgentEvalReportJsonSerializer()
        self.markdown_renderer = markdown_renderer or AgentEvalReportMarkdownRenderer()

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
                self.json_serializer.serialize(
                    report, quality_gate_result=quality_gate_result
                ),
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
            self.markdown_renderer.render(
                report, quality_gate_result=quality_gate_result
            ),
            encoding="utf-8",
        )
        return resolved_path
