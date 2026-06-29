from __future__ import annotations

from typing import Any

from src.application.langgraph.common import GraphError
from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    format_document_options,
    serialize_tool_result,
)
from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.common import ToolResult
from src.application.tools.documents import (
    DocumentDetailsRequest,
    FindDocumentRequest,
    ListDocumentsRequest,
)
from src.application.tools.evaluation import (
    RetrievalTraceRequest,
    RunQualityGateRequest,
)
from src.application.tools.exploration import ExploreDocumentRequest
from src.application.tools.question_answering import AnswerQuestionRequest
from src.application.tools.retrieval import RetrieveChunksRequest


class PlanExecutor:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def execute(
        self,
        plan: ExecutionPlan,
        state: AgentState,
        tool_registry: ToolRegistry,
    ) -> AgentState:
        next_state: AgentState = dict(state)  # type: ignore[assignment]
        tool_results = dict(next_state.get("tool_results", {}))
        trace = list(next_state.get("trace", []))
        step_outputs: dict[str, dict[str, Any]] = {}
        executed_steps: list[str] = []
        failed_step: str | None = None
        plan_success = True

        for step in plan.steps:
            if not self._dependencies_satisfied(step.depends_on, step_outputs):
                failed_step = step.step_id
                plan_success = False
                next_state["error"] = build_error(
                    message="Plan step dependencies were not satisfied.",
                    error_code="plan_dependency_failed",
                    diagnostics={
                        "plan_id": plan.plan_id,
                        "step_id": step.step_id,
                        "depends_on": step.depends_on,
                    },
                )
                break

            resolved_document_id = self._resolved_document_id(next_state)
            token = self.recorder.start_node(
                "plan_step",
                route=next_state.get("route"),
                tool_name=step.tool_name,
                plan_id=plan.plan_id,
                plan_goal=plan.goal,
                step_id=step.step_id,
                selected_document_id=resolved_document_id,
            )
            try:
                result = self._execute_step(
                    step=step,
                    state=next_state,
                    tool_registry=tool_registry,
                    step_outputs=step_outputs,
                )
            except GraphError as exc:
                result = ToolResult.fail(
                    exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                )
            serialized = serialize_tool_result(result)
            serialized["tool_name"] = step.tool_name
            serialized["step_id"] = step.step_id
            tool_results[step.output_key] = serialized
            self._store_canonical_tool_result(
                tool_results=tool_results,
                tool_name=step.tool_name,
                serialized=serialized,
            )
            step_outputs[step.output_key] = {
                "tool_name": step.tool_name,
                "success": serialized["success"],
                "data": serialized.get("data"),
                "message": serialized.get("message"),
                "error_code": serialized.get("error_code"),
            }
            executed_steps.append(step.step_id)
            trace.append(
                self.recorder.finish_node(
                    token,
                    success=result.success,
                    error_code=result.error_code,
                    diagnostics=result.diagnostics,
                )
            )

            next_state["tool_results"] = tool_results
            next_state["trace"] = trace
            self._apply_success_state(
                next_state=next_state,
                step=step,
                result=result,
                step_outputs=step_outputs,
            )

            if result.success:
                continue

            failed_step = step.step_id
            plan_success = False
            if self._apply_failure_state(
                next_state=next_state,
                step=step,
                result=result,
            ):
                break
            if step.required:
                break

        next_state["execution_plan"] = plan.to_dict()
        next_state["plan_steps"] = [step.to_dict() for step in plan.steps]
        next_state["plan_success"] = plan_success
        next_state["failed_plan_step"] = failed_step
        next_state["plan_results"] = serialize_graph_value(
            {
                "plan_id": plan.plan_id,
                "goal": plan.goal,
                "executed_steps": executed_steps,
                "failed_step": failed_step,
                "plan_success": plan_success,
                "step_outputs": step_outputs,
                "plan_kind": plan.diagnostics.get("plan_kind"),
                "final_response_text": next_state.get("response_text"),
            }
        )
        return next_state

    @staticmethod
    def _dependencies_satisfied(
        depends_on: list[str],
        step_outputs: dict[str, dict[str, Any]],
    ) -> bool:
        return all(
            dependency in step_outputs
            and bool(step_outputs[dependency].get("success"))
            for dependency in depends_on
        )

    @staticmethod
    def _resolved_document_id(state: AgentState) -> str | None:
        return state.get("document_id") or state.get("selected_document_id")

    def _execute_step(
        self,
        *,
        step: Any,
        state: AgentState,
        tool_registry: ToolRegistry,
        step_outputs: dict[str, dict[str, Any]],
    ) -> ToolResult:
        if step.tool_name == "format_combined_answer":
            return self._format_combined_answer(step=step, step_outputs=step_outputs)

        tool = tool_registry.require(step.tool_name)
        request = self._build_request(
            step=step,
            state=state,
        )
        return tool.run(request)

    def _build_request(self, *, step, state: AgentState):
        document_id = self._resolved_document_id(state)
        args = step.args
        if step.tool_name == "list_documents":
            return ListDocumentsRequest()
        if step.tool_name == "find_document":
            query_text = args.get("query_text") or state.get("document_query")
            document_selector = state.get("document_id") if not query_text else None
            return FindDocumentRequest(
                document_id=document_selector,
                query_text=query_text,
            )
        if step.tool_name == "document_details":
            return DocumentDetailsRequest(document_id=document_id)
        if step.tool_name == "explore_document":
            return ExploreDocumentRequest(document_id=document_id)
        if step.tool_name == "retrieve_chunks":
            return RetrieveChunksRequest(
                query_text=str(args.get("query_text") or state.get("question") or state["user_input"]),
                document_id=document_id,
                top_k=state.get("top_k") or 5,
            )
        if step.tool_name == "answer_question":
            return AnswerQuestionRequest(
                question=str(args.get("question") or state.get("question") or state["user_input"]),
                document_id=document_id,
                top_k=state.get("top_k"),
                allow_answer_generation=state["allow_answer_generation"],
                include_context=state["include_context"],
                require_citations=True,
            )
        if step.tool_name == "run_quality_gate":
            return RunQualityGateRequest(
                report_path=args.get("report_path"),
                thresholds_path=args.get("thresholds_path"),
            )
        if step.tool_name == "retrieval_trace":
            return RetrievalTraceRequest(
                query_text=str(args.get("query_text") or state.get("question") or state["user_input"]),
                document_id=document_id,
                top_k=state.get("top_k") or 5,
                write_output=bool(args.get("write_output", True)),
            )
        raise ValueError(f"Unsupported plan tool: {step.tool_name}")

    @staticmethod
    def _store_canonical_tool_result(
        *,
        tool_results: dict[str, Any],
        tool_name: str,
        serialized: dict[str, Any],
    ) -> None:
        canonical_key = {
            "retrieve_chunks": "retrieve_evidence",
        }.get(tool_name, tool_name)
        tool_results[canonical_key] = serialized

    def _apply_success_state(
        self,
        *,
        next_state: AgentState,
        step,
        result: ToolResult,
        step_outputs: dict[str, dict[str, Any]],
    ) -> None:
        if not result.success:
            return
        if step.tool_name == "find_document":
            data = result.data or {}
            if isinstance(data, dict):
                title = data.get("display_name") or data.get("title")
                next_state["document_id"] = data.get("document_id")
                next_state["document_title"] = title
                next_state["selected_document_id"] = data.get("document_id")
                next_state["selected_document_title"] = title
                next_state["selected_document_file_name"] = data.get("file_name")
                next_state["needs_clarification"] = False
                next_state["clarification_message"] = None
                next_state["pending_clarification"] = None
                next_state["clarification_options"] = []
                next_state["clarification_question"] = None
                next_state["clarification_candidate_index"] = None
        elif step.tool_name == "format_combined_answer":
            data = result.data or {}
            if isinstance(data, dict):
                next_state["response_text"] = data.get("text")
        elif step.tool_name == "answer_question":
            payload = step_outputs.get(step.output_key, {}).get("data")
            if isinstance(payload, dict):
                next_state["response_text"] = (
                    payload.get("answer_text")
                    or payload.get("safe_user_message")
                    or next_state.get("response_text")
                )

    def _apply_failure_state(
        self,
        *,
        next_state: AgentState,
        step,
        result: ToolResult,
    ) -> bool:
        if step.tool_name == "find_document":
            if result.error_code == "multiple_documents_found":
                matches = result.diagnostics.get("matches", [])
                next_state["needs_clarification"] = True
                next_state["clarification_options"] = matches if isinstance(matches, list) else []
                next_state["clarification_question"] = (
                    "I found multiple matching documents. Which one do you mean?"
                )
                next_state["pending_clarification"] = {
                    "kind": "document_selection",
                    "route": next_state.get("route"),
                }
                next_state["clarification_message"] = format_document_options(
                    next_state["clarification_options"]
                )
                next_state["response_text"] = next_state["clarification_message"]
                return True
            if result.error_code == "document_not_found":
                next_state["needs_clarification"] = True
                next_state["clarification_message"] = (
                    "I could not find that document. Please refine the document name or ID."
                )
                next_state["response_text"] = next_state["clarification_message"]
                return True

        next_state["error"] = build_error(
            message=result.message or "Plan step failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics={
                "tool_name": step.tool_name,
                "step_id": step.step_id,
                **dict(result.diagnostics or {}),
            },
        )
        return True

    @staticmethod
    def _format_combined_answer(*, step, step_outputs: dict[str, dict[str, Any]]) -> ToolResult:
        labels = list(step.args.get("section_labels", []))
        sections: list[str] = []
        for index, dependency in enumerate(step.depends_on):
            label = labels[index] if index < len(labels) else f"Section {index + 1}"
            payload = step_outputs.get(dependency, {}).get("data")
            body = PlanExecutor._extract_answer_text(payload)
            sections.append(f"{label}:\n{body}")
        body_text = "\n\n".join(sections).strip()
        if body_text:
            summary = "Comparison summary: both sections were answered from the selected document."
            text = f"{body_text}\n\n{summary}"
        else:
            text = "No combined answer could be produced."
        return ToolResult.ok(data={"text": text})

    @staticmethod
    def _extract_answer_text(payload: Any) -> str:
        if isinstance(payload, dict):
            return (
                str(payload.get("answer_text") or "")
                or str(payload.get("safe_user_message") or "")
                or str(payload.get("response_text") or "")
            ).strip() or "No answer was available."
        return "No answer was available."
