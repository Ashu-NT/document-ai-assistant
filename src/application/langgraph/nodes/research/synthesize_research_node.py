from __future__ import annotations

from src.application.langgraph.nodes.node_utils import build_error, extend_trace
from src.application.langgraph.research import ResearchService
from src.application.langgraph.research.services import ResearchStateMapper
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.shared.exceptions import SchemaValidationError


class SynthesizeResearchNode:
    def __init__(
        self,
        research_service: ResearchService,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.research_service = research_service
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "synthesize_research",
            route=state.get("route"),
        )
        result = ResearchStateMapper.result_from_state(state)
        if result is None:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="research_result_missing",
            )
            return {
                "error": build_error(
                    message="Research synthesis could not run because no research result was available.",
                    error_code="research_result_missing",
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        try:
            result = self.research_service.synthesize_research(result)
        except SchemaValidationError as exc:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=exc.error_code,
                diagnostics=exc.details or {},
            )
            return {
                "error": build_error(
                    message=exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        research_trace = dict(state.get("research_trace") or {})
        if result.report is not None:
            research_trace["final_report_sections"] = [
                str(section.get("title") or "Section")
                for section in result.report.sections
                if isinstance(section, dict)
            ]
        research_trace["synthesis_model"] = "deterministic"
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "report_title": result.report.title if result.report is not None else None,
                "section_count": len(result.report.sections) if result.report is not None else 0,
            },
        )
        return {
            **ResearchStateMapper.result_to_state(result),
            "research_trace": research_trace,
            "trace": extend_trace(state["trace"], trace_entry),
        }
