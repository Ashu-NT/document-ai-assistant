from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_step import PlanStep
from src.shared.ids import IdGenerator


@dataclass(slots=True, frozen=True)
class PlanParseResult:
    success: bool
    plan: ExecutionPlan | None = None
    error_code: str | None = None
    message: str | None = None
    raw_text: str = ""
    diagnostics: dict[str, Any] = field(default_factory=dict)


class PlanParser:
    def __init__(self, *, id_generator: IdGenerator | None = None) -> None:
        self.id_generator = id_generator or IdGenerator()

    def parse(self, raw_text: str) -> PlanParseResult:
        cleaned = self._strip_code_fences(raw_text)
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            return PlanParseResult(
                success=False,
                error_code="plan_json_invalid",
                message="The LLM planning output was not valid JSON.",
                raw_text=raw_text,
                diagnostics={"error": str(exc)},
            )

        if not isinstance(payload, dict):
            return PlanParseResult(
                success=False,
                error_code="plan_shape_invalid",
                message="The LLM planning output must be a JSON object.",
                raw_text=raw_text,
            )

        steps_payload = payload.get("steps")
        if not isinstance(steps_payload, list) or not steps_payload:
            return PlanParseResult(
                success=False,
                error_code="plan_steps_missing",
                message="The LLM plan must contain at least one step.",
                raw_text=raw_text,
            )

        try:
            plan = self._build_plan(payload)
        except (KeyError, TypeError, ValueError) as exc:
            return PlanParseResult(
                success=False,
                error_code="plan_shape_invalid",
                message="The LLM plan had an invalid structure.",
                raw_text=raw_text,
                diagnostics={"error": str(exc)},
            )

        return PlanParseResult(
            success=True,
            plan=plan,
            raw_text=raw_text,
            diagnostics={"step_count": plan.step_count},
        )

    def _build_plan(self, payload: dict[str, Any]) -> ExecutionPlan:
        raw_steps = payload["steps"]
        steps: list[PlanStep] = []
        for index, raw_step in enumerate(raw_steps, start=1):
            if not isinstance(raw_step, dict):
                raise TypeError("Each plan step must be an object.")
            step_id = str(raw_step.get("step_id") or f"step_{index}")
            output_key = str(raw_step.get("output_key") or f"step_output_{index}")
            steps.append(
                PlanStep(
                    step_id=step_id,
                    tool_name=str(raw_step["tool_name"]),
                    description=str(raw_step["description"]),
                    input_key=raw_step.get("input_key"),
                    output_key=output_key,
                    args=dict(raw_step.get("args", {})),
                    depends_on=[str(item) for item in list(raw_step.get("depends_on", []))],
                    required=bool(raw_step.get("required", True)),
                    source="llm",
                )
            )

        return ExecutionPlan(
            plan_id=str(payload.get("plan_id") or self.id_generator.new_id("plan")),
            goal=str(payload["goal"]),
            steps=steps,
            reason=str(payload.get("reason") or "LLM-proposed plan."),
            source="llm",
            requires_document=bool(payload.get("requires_document", False)),
            document_id=_optional_str(payload.get("document_id")),
            document_title=_optional_str(payload.get("document_title")),
            diagnostics=dict(payload.get("diagnostics", {})),
        )

    @staticmethod
    def _strip_code_fences(raw_text: str) -> str:
        stripped = raw_text.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                return "\n".join(lines[1:-1]).strip()
        return stripped


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None
