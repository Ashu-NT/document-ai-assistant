from __future__ import annotations

from src.application.langgraph.common import GraphError
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    extend_trace,
    serialize_tool_result,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.question_answering import AnswerQuestionRequest


class AnswerQuestionNode:
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
            "answer_question",
            route=state.get("route"),
            tool_name="answer_question",
        )
        try:
            tool = self.tool_registry.require("answer_question")
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

        question = state.get("question") or state["user_input"].strip()
        result = tool.run(
            AnswerQuestionRequest(
                question=question,
                document_id=state.get("document_id"),
                top_k=state.get("top_k"),
                allow_answer_generation=state["allow_answer_generation"],
                include_context=state["include_context"],
                require_citations=True,
            )
        )
        tool_results = dict(state["tool_results"])
        tool_results["answer_question"] = serialize_tool_result(result)
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
            qa_result = result.data
            patch["response_text"] = getattr(qa_result, "answer_text", None) or getattr(
                qa_result,
                "safe_user_message",
                None,
            )
            return patch

        patch["error"] = build_error(
            message=result.message or "Question answering failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch
