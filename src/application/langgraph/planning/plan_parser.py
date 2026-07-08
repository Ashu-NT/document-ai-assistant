from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_response_schema import (
    PlanResponsePayload,
)
from src.application.langgraph.planning.plan_step import PlanStep
from src.shared.ids import IdGenerator
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)
from pydantic import ValidationError


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
        cleaned = strip_code_fences_if_wrapped(raw_text)
        try:
            payload = PlanResponsePayload.model_validate_json(cleaned)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                return PlanParseResult(
                    success=False,
                    error_code="plan_json_invalid",
                    message="The LLM planning output was not valid JSON.",
                    raw_text=raw_text,
                    diagnostics={"errors": exc.errors()},
                )
            if self._is_steps_missing_error(exc):
                return PlanParseResult(
                    success=False,
                    error_code="plan_steps_missing",
                    message="The LLM plan must contain at least one step.",
                    raw_text=raw_text,
                    diagnostics={"errors": exc.errors()},
                )
            return PlanParseResult(
                success=False,
                error_code="plan_shape_invalid",
                message="The LLM plan had an invalid structure.",
                raw_text=raw_text,
                diagnostics={"errors": exc.errors()},
            )
        except ValueError as exc:
            return PlanParseResult(
                success=False,
                error_code="plan_json_invalid",
                message="The LLM planning output was not valid JSON.",
                raw_text=raw_text,
                diagnostics={"error": str(exc)},
            )
        plan = self._build_plan(payload)

        return PlanParseResult(
            success=True,
            plan=plan,
            raw_text=raw_text,
            diagnostics={"step_count": plan.step_count},
        )

    def _build_plan(self, payload: PlanResponsePayload) -> ExecutionPlan:
        steps: list[PlanStep] = []
        for index, raw_step in enumerate(payload.steps, start=1):
            step_id = raw_step.step_id or f"step_{index}"
            output_key = raw_step.output_key or f"step_output_{index}"
            steps.append(
                PlanStep(
                    step_id=step_id,
                    tool_name=raw_step.tool_name,
                    description=raw_step.description,
                    input_key=raw_step.input_key,
                    output_key=output_key,
                    args=dict(raw_step.args),
                    depends_on=list(raw_step.depends_on),
                    required=raw_step.required,
                    source="llm",
                )
            )

        return ExecutionPlan(
            plan_id=payload.plan_id or self.id_generator.new_id("plan"),
            goal=payload.goal,
            steps=steps,
            reason=payload.reason or "LLM-proposed plan.",
            source="llm",
            requires_document=payload.requires_document,
            document_id=payload.document_id,
            document_title=payload.document_title,
            diagnostics=dict(payload.diagnostics),
        )

    @staticmethod
    def _is_steps_missing_error(exc: ValidationError) -> bool:
        return any(error.get("loc") == ("steps",) for error in exc.errors())
