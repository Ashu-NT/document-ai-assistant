from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from src.application.langgraph.common import serialize_graph_value

if TYPE_CHECKING:
    from src.application.langgraph.evaluation.agent_eval_result import AgentEvalReport


class AgentEvalReportJsonSerializer:
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
