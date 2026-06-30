from __future__ import annotations

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalPlan,
    RetrievalPlanStep,
    RetrievalStrategy,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)

_SAFE_RETRIEVAL_TOOLS = {
    "retrieve_chunks",
    "retrieve_identifiers",
    "retrieve_tables",
    "retrieve_figures",
}


class RetrievalPlanValidator:
    def validate(
        self,
        plan: RetrievalPlan,
        *,
        tool_registry: ToolRegistry,
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalPlan:
        validated_steps: list[RetrievalPlanStep] = []
        seen_output_keys: set[str] = set()
        diagnostics = dict(plan.diagnostics)
        fallbacks: list[str] = []

        for step in plan.steps[: policy.max_strategies_per_query]:
            if step.output_key in seen_output_keys:
                step.output_key = f"{step.output_key}_{len(seen_output_keys) + 1}"
            seen_output_keys.add(step.output_key)

            if step.top_k <= 0 or step.top_k > policy.max_top_k:
                step.top_k = min(max(step.top_k, 1), policy.max_top_k)

            if plan.document_id is not None:
                step.document_id = plan.document_id

            if step.tool_name not in _SAFE_RETRIEVAL_TOOLS:
                step = self._fallback_step(step)
                fallbacks.append(f"{step.step_id}:unsafe_tool")
            elif tool_registry.maybe(step.tool_name) is None:
                fallback = self._fallback_step(step)
                if fallback.tool_name != step.tool_name:
                    fallbacks.append(f"{step.step_id}:{step.tool_name}->retrieve_chunks")
                step = fallback

            validated_steps.append(step)

        diagnostics["validator_fallbacks"] = fallbacks
        return RetrievalPlan(
            plan_id=plan.plan_id,
            original_query=plan.original_query,
            document_id=plan.document_id,
            steps=validated_steps,
            primary_strategy=plan.primary_strategy,
            reason=plan.reason,
            diagnostics=diagnostics,
        )

    @staticmethod
    def _fallback_step(step: RetrievalPlanStep) -> RetrievalPlanStep:
        if step.tool_name == "retrieve_chunks":
            return step
        return RetrievalPlanStep(
            step_id=step.step_id,
            strategy=step.strategy,
            query=step.query,
            document_id=step.document_id,
            top_k=step.top_k,
            tool_name="retrieve_chunks",
            args={
                "query_text": step.query,
                "document_id": step.document_id,
                "top_k": step.top_k,
                "chunk_types": list(step.args.get("chunk_types", [])),
            },
            output_key=step.output_key,
            required=step.required,
            reason=(
                f"{step.reason} Fallback to retrieve_chunks because {step.tool_name} "
                "is unavailable."
            ).strip(),
        )
