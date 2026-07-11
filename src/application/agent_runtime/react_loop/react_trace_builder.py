from __future__ import annotations

from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_event import ReactEvent
from src.application.agent_runtime.react_loop.react_step import ReactStep
from src.application.agent_runtime.react_loop.react_trace import ReactTrace
from src.application.agent_runtime.react_loop.trace_sections.action_step_formatter import (
    format_action_steps,
)
from src.application.agent_runtime.react_loop.trace_sections.guardrail_message_formatter import (
    format_guardrail_message,
)
from src.application.agent_runtime.react_loop.trace_sections.observation_formatter import (
    format_observation,
)
from src.application.agent_runtime.react_loop.trace_sections.plan_step_formatter import (
    format_plan_steps,
    format_research_plan,
)
from src.application.agent_runtime.react_loop.trace_sections.reflection_formatter import (
    format_reflection,
)
from src.application.agent_runtime.react_loop.trace_sections.retrieval_strategy_formatter import (
    format_retrieval_strategy,
)
from src.application.agent_runtime.react_loop.trace_sections.thought_summary_formatter import (
    format_thought_summary,
)


class ReactTraceBuilder:
    def build(
        self,
        *,
        user_input: str,
        result,
        policy: DemoVisibilityPolicy,
    ) -> ReactTrace:
        data = result.data or {}
        trace = ReactTrace(
            route=result.route,
            final_answer=data.get("answer") or result.response_text,
        )
        self._append(
            trace,
            ReactEvent.THOUGHT_SUMMARY,
            "Thought Summary",
            format_thought_summary(result.route, data, user_input),
        )
        if result.route == "out_of_scope":
            self._append(
                trace,
                ReactEvent.GUARDRAIL,
                "Guardrail",
                format_guardrail_message(data, result.response_text),
            )
            return trace
        if result.route == "blocked_action" or data.get("unsafe_request_blocked"):
            self._append(
                trace,
                ReactEvent.SAFETY_BLOCK
                if data.get("unsafe_request_blocked")
                else ReactEvent.GUARDRAIL,
                "Safety Block" if data.get("unsafe_request_blocked") else "Guardrail",
                format_guardrail_message(data, result.response_text),
            )
            return trace
        if isinstance(data.get("execution_plan"), dict) and data.get("plan_steps"):
            self._append(
                trace,
                ReactEvent.PLAN,
                "Plan",
                format_plan_steps(data.get("plan_steps")),
            )
        if policy.show_research_plan and isinstance(data.get("research_plan"), dict):
            research_body = format_research_plan(data.get("research_plan"))
            if research_body:
                self._append(
                    trace,
                    ReactEvent.RESEARCH_PLAN,
                    "Research Plan",
                    research_body,
                )
        if policy.show_retrieval_strategy:
            retrieval_body = format_retrieval_strategy(data)
            if retrieval_body:
                self._append(
                    trace,
                    ReactEvent.RETRIEVAL_STRATEGY,
                    "Retrieval Strategy",
                    retrieval_body,
                )
        if policy.show_tools:
            action_body = format_action_steps(result.trace or [])
            if action_body:
                self._append(
                    trace,
                    ReactEvent.ACTION,
                    "Action",
                    action_body,
                )
        if policy.show_observations:
            observation_body = format_observation(data, max_chars=policy.max_observation_chars)
            if observation_body:
                self._append(
                    trace,
                    ReactEvent.OBSERVATION,
                    "Observation",
                    observation_body,
                )
        if policy.show_reflection:
            reflection_body = format_reflection(data)
            if reflection_body:
                self._append(
                    trace,
                    ReactEvent.REFLECTION,
                    "Reflection",
                    reflection_body,
                )
        if not result.success and result.response_text:
            self._append(
                trace,
                ReactEvent.ERROR,
                "Error",
                str(result.response_text).strip(),
            )
        return trace

    def _append(
        self,
        trace: ReactTrace,
        event_type: ReactEvent,
        title: str,
        body: str,
    ) -> None:
        normalized = body.strip()
        if not normalized:
            return
        trace.steps.append(
            ReactStep(
                index=len(trace.steps) + 1,
                event_type=event_type,
                title=title,
                body=normalized,
            )
        )
