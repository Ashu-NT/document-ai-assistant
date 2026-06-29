from __future__ import annotations

from time import perf_counter
from typing import Any

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.planning.plan_policy import PlanPolicy
from src.application.langgraph.planning.plan_prompt_builder import (
    PLANNING_PROMPT_VERSION,
    PlanPromptBuilder,
)
from src.application.langgraph.routing import RouteDecision
from src.application.langgraph.state import AgentState
from src.application.services.ai import LLMService


class LLMPlanProposer:
    def __init__(
        self,
        llm_service: LLMService,
        *,
        prompt_builder: PlanPromptBuilder | None = None,
        model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or PlanPromptBuilder()
        self.model = model
        self._last_diagnostics: dict[str, Any] = {}

    @property
    def last_diagnostics(self) -> dict[str, Any]:
        return dict(self._last_diagnostics)

    def propose(
        self,
        state: AgentState,
        route_decision: RouteDecision,
        tool_registry: ToolRegistry,
        policy: PlanPolicy,
    ) -> str:
        prompt = self.prompt_builder.build(
            user_input=state["user_input"],
            state=state,
            route_decision=route_decision,
            tool_registry=tool_registry,
            policy=policy,
        )
        started = perf_counter()
        raw_text = self.llm_service.generate(prompt, model=self.model)
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        self._last_diagnostics = {
            "model_used": self.model,
            "prompt_version": PLANNING_PROMPT_VERSION,
            "elapsed_ms": elapsed_ms,
        }
        return raw_text
