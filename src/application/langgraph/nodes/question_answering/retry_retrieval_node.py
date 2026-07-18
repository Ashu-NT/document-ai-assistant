from __future__ import annotations

from src.application.langgraph.common import (
    GraphError,
    resolve_state_response_text,
    serialize_graph_value,
)
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    deserialize_identifiers,
    extend_trace,
    extract_retrieval_query_intent,
)
from src.application.langgraph.nodes.question_answering.mappers.retrieved_chunk_state_mapper import (
    dict_to_chunk,
)
from src.application.langgraph.nodes.question_answering.retry_retrieval_node_helpers import (
    current_primary_strategy,
    decision_from_state,
    extract_answer_intent,
)
from src.application.langgraph.nodes.question_answering.retry_retrieval_strategy_executor import (
    execute_retry_strategy_plan,
)
from src.application.langgraph.retrieval_strategy import (
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
)
from src.application.langgraph.reflection import EvidenceMerger, RetrievalRetryPolicy
from src.application.langgraph.reflection.strategies.retry_reformulation import (
    RetryReformulationContext,
    RetryReformulationStrategyRegistry,
)
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.question_answering import AnswerQuestionRequest
from src.application.tools.retrieval import RetrieveChunksRequest


class RetryRetrievalNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        evidence_merger: EvidenceMerger | None = None,
        retry_reformulation_registry: RetryReformulationStrategyRegistry | None = None,
        retry_policy: RetrievalRetryPolicy | None = None,
        retrieval_strategy_service: RetrievalStrategyService | None = None,
        retrieval_plan_executor: RetrievalPlanExecutor | None = None,
        retrieval_strategy_policy: RetrievalStrategyPolicy | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.evidence_merger = evidence_merger or EvidenceMerger()
        self.retry_reformulation_registry = (
            retry_reformulation_registry or RetryReformulationStrategyRegistry()
        )
        self.retry_policy = retry_policy or RetrievalRetryPolicy()
        self.retrieval_strategy_service = retrieval_strategy_service
        self.retrieval_plan_executor = retrieval_plan_executor
        self.retrieval_strategy_policy = (
            retrieval_strategy_policy or RetrievalStrategyPolicy()
        )
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "retry_retrieval",
            route=state.get("route"),
        )
        if state.get("route") == RouteType.DEEP_RESEARCH.value:
            trace_entry = self.recorder.finish_node(
                token,
                success=True,
                diagnostics={"skipped": "deep_research"},
            )
            return {
                "response_text": resolve_state_response_text(state)
                or state.get("response_text"),
                "trace": extend_trace(state["trace"], trace_entry),
            }
        try:
            retrieve_tool = self.tool_registry.require("retrieve_chunks")
            answer_tool = self.tool_registry.require("answer_question")
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

        reflection_result = state.get("reflection_result") or {}
        decision = (reflection_result.get("decision") or {}) if isinstance(reflection_result, dict) else {}
        reason = str(decision.get("reason") or "Reflection requested a retrieval retry.")
        retry_top_k = self._retry_top_k(state.get("top_k"))
        # An already-set state["retry_query"] (reflect_answer_node stashes
        # the LLM/decider's own suggested retry_query there) takes
        # precedence over anything the decision dict itself carries -- fed
        # into the SAME reformulation call so its relatedness check and the
        # retrieval-strategy hint are both derived from one consistent
        # source, instead of two separately-triggered keyword scanners.
        decision_payload = dict(decision)
        if not decision_payload.get("retry_query") and state.get("retry_query"):
            decision_payload["retry_query"] = state.get("retry_query")
        retry_plan = self.retry_reformulation_registry.build_retry_plan(
            retrieval_query_intent=extract_retrieval_query_intent(
                (state.get("tool_results", {}).get("answer_question") or {})
                .get("data", {})
                .get("retrieval_result")
            ),
            context=RetryReformulationContext(
                original_user_question=state.get("question") or state["user_input"],
                answer_intent=extract_answer_intent(state),
                selected_document_id=state.get("selected_document_id")
                or state.get("document_id"),
                reflection_decision=decision_from_state(decision_payload, reason),
                top_k=retry_top_k,
                current_primary_strategy=current_primary_strategy(state),
            ),
        )
        retry_query = retry_plan.retry_query
        resolved_identifiers = deserialize_identifiers(state.get("resolved_identifiers"))
        existing_structured_entities = state.get("resolved_structured_entities")
        resolved_structured_entities = list(existing_structured_entities) if isinstance(
            existing_structured_entities, list
        ) else []

        strategy_outcome = execute_retry_strategy_plan(
            state=state,
            retry_query=retry_query,
            retry_top_k=retry_top_k,
            reason=reason,
            retry_plan=retry_plan,
            resolved_identifiers=resolved_identifiers,
            tool_registry=self.tool_registry,
            retrieval_strategy_policy=self.retrieval_strategy_policy,
            retrieval_strategy_service=self.retrieval_strategy_service,
            retrieval_plan_executor=self.retrieval_plan_executor,
        )
        retry_result = strategy_outcome.retry_result
        resolved_identifiers = strategy_outcome.resolved_identifiers
        strategy_patch = strategy_outcome.strategy_patch

        if retry_result is None:
            retry_result = retrieve_tool.run(
                RetrieveChunksRequest(
                    query_text=retry_query,
                    document_id=state.get("selected_document_id") or state.get("document_id"),
                    top_k=retry_top_k,
                )
            )
        if not retry_result.success:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=retry_result.error_code,
                diagnostics=retry_result.diagnostics,
            )
            return {
                "reflection_decision": "FAIL",
                # Cleared alongside the decision (mirrors the success-path
                # clearing below) -- otherwise the PREVIOUS reflection
                # pass's score/reason (the one whose RETRIEVE_AGAIN
                # triggered this retry) would still be in state and get
                # rendered to the user as if it described this failure.
                "reflection_result": None,
                "reflection_score": None,
                "response_text": "I could not gather better evidence on retry.",
                "trace": extend_trace(state["trace"], trace_entry),
            }

        retry_data = retry_result.data or {}
        retry_chunks = list(retry_data.get("context_chunks", []) or [])
        initial_chunks = [dict_to_chunk(item) for item in state.get("initial_context_chunks", [])]
        merged_chunks, merge_diagnostics = self.evidence_merger.merge(
            initial_chunks=initial_chunks,
            retry_chunks=retry_chunks,
            policy=self.retry_policy,
            document_id=state.get("selected_document_id") or state.get("document_id"),
        )
        regenerated = answer_tool.run(
            AnswerQuestionRequest(
                question=state.get("question") or state["user_input"],
                document_id=state.get("selected_document_id") or state.get("document_id"),
                top_k=state.get("top_k"),
                allow_answer_generation=state["allow_answer_generation"],
                include_context=state["include_context"],
                require_citations=True,
                context_override_chunks=merged_chunks,
                retry_query=retry_query,
                resolved_identifiers=resolved_identifiers,
                resolved_structured_entities=resolved_structured_entities,
            )
        )
        tool_results = dict(state["tool_results"])
        tool_results["retry_retrieval"] = serialize_graph_value(
            {
                "success": retry_result.success,
                "data": retry_data,
                "diagnostics": retry_result.diagnostics,
            }
        )
        if regenerated.success:
            tool_results["answer_question"] = serialize_graph_value(
                {
                    "success": regenerated.success,
                    "data": regenerated.data,
                    "diagnostics": regenerated.diagnostics,
                }
            )
        trace_entry = self.recorder.finish_node(
            token,
            success=regenerated.success,
            diagnostics=merge_diagnostics,
        )
        patch = {
            "tool_results": tool_results,
            "retrieval_retry_count": int(state.get("retrieval_retry_count", 0)) + 1,
            "retry_query": retry_query,
            "retry_context_chunks": serialize_graph_value(retry_chunks),
            "merged_context_chunks": serialize_graph_value(merged_chunks),
            "merged_chunk_ids": [chunk.chunk_id for chunk in merged_chunks],
            "resolved_identifiers": serialize_graph_value(resolved_identifiers),
            "resolved_structured_entities": serialize_graph_value(
                resolved_structured_entities
            ),
            "trace": extend_trace(state["trace"], trace_entry),
            **strategy_patch,
        }
        if regenerated.success:
            qa_result = regenerated.data
            qa_identifiers = getattr(
                qa_result,
                "resolved_identifiers",
                resolved_identifiers,
            )
            qa_structured_entities = getattr(
                qa_result,
                "resolved_structured_entities",
                resolved_structured_entities,
            )
            patch["response_text"] = getattr(qa_result, "answer_text", None) or getattr(
                qa_result,
                "safe_user_message",
                None,
            )
            patch["resolved_identifiers"] = serialize_graph_value(qa_identifiers)
            patch["resolved_structured_entities"] = serialize_graph_value(
                qa_structured_entities
            )
            patch["reflection_decision"] = None
            patch["reflection_result"] = None
            patch["reflection_score"] = None
            return patch

        patch["response_text"] = "I could not regenerate a grounded answer after retry."
        patch["reflection_decision"] = "FAIL"
        # Same staleness fix as the retrieve-tool-failure path above: the
        # previous reflection pass's score/reason must not survive to be
        # rendered alongside this failure.
        patch["reflection_result"] = None
        patch["reflection_score"] = None
        return patch

    def _retry_top_k(self, current_top_k: int | None) -> int:
        base = current_top_k or 5
        if self.retry_policy.increase_top_k_on_retry:
            return base + self.retry_policy.retry_top_k_increment
        return base
