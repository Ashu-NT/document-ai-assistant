from __future__ import annotations

from pathlib import Path

from src.application.langgraph.common import GraphError
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    extend_trace,
    serialize_tool_result,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.evaluation import RunQualityGateRequest


class RunQualityGateNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "run_quality_gate",
            route=state.get("route"),
            tool_name="run_quality_gate",
        )
        try:
            tool = self.tool_registry.require("run_quality_gate")
        except GraphError as exc:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=exc.error_code,
                diagnostics=exc.details,
            )
            return {
                "error": build_error(
                    message=exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        result = tool.run(
            RunQualityGateRequest(
                report_path=str(_default_report_path()),
            )
        )
        tool_results = dict(state["tool_results"])
        tool_results["run_quality_gate"] = serialize_tool_result(result)
        trace_entry = self.recorder.finish_node(
            token,
            success=result.success,
            error_code=result.error_code,
            diagnostics=result.diagnostics,
        )
        patch = {
            "tool_results": tool_results,
            "trace": extend_trace(state["trace"], trace_entry),
        }
        if result.success:
            payload = result.data or {}
            patch["response_text"] = payload.get("summary") or "Quality gate passed."
            return patch

        patch["error"] = build_error(
            message=result.message or "Quality gate failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics or result.data or {},
        )
        return patch


def _default_report_path() -> Path:
    from src.config.settings import storage_settings

    return storage_settings.evaluation_output_path / "retrieval" / "retrieval_benchmark_report.json"
