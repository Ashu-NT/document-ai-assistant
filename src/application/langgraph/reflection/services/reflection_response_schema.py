from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.application.langgraph.reflection.models import ReflectionDecisionType


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


class ReflectionResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: ReflectionDecisionType
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str
    retry_query: str | None = None
    clarification_question: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    # True only for a HARD grounding failure (the answer states something
    # not supported by, or contradicted by, the approved evidence) -- not
    # for merely incomplete evidence. This is the signal
    # ReflectionValidator's domain-specific downgrade paths (e.g. "grounded
    # maintenance interval evidence exists, so accept anyway") gate on, so a
    # false positive here would block a legitimate downgrade and a false
    # negative would let a genuinely wrong answer through. Previously this
    # signal never reached the validator for any LLM-sourced decision.
    grounding_violation: bool = Field(default=False)
    # Graded claim-to-evidence faithfulness (W9,
    # answering_flow_weakness_remediation_plan.md): 1.0 = every claim in the
    # answer is directly supported by the approved evidence, 0.0 = the
    # answer is unsupported/contradicted throughout. Unlike
    # `grounding_violation` (a binary hard-failure flag used to gate
    # decisions), this is a graded signal that replaces AnswerQualityScorer's
    # lexical-proxy score with a real entailment judgment whenever the
    # reflection LLM call succeeds.
    entailment_score: float = Field(default=1.0, ge=0.0, le=1.0)
    # Specific claims the LLM judged unsupported -- empty when
    # entailment_score is 1.0. Surfaced for diagnostics/observability, not
    # used to gate any decision by itself.
    unsupported_claims: list[str] = Field(default_factory=list)

    @field_validator("decision", mode="before")
    @classmethod
    def _validate_decision(cls, value: Any) -> Any:
        text = _optional_text(value)
        return text.upper() if text else text

    @field_validator("reason", "retry_query", "clarification_question", mode="before")
    @classmethod
    def _validate_text_fields(cls, value: Any) -> Any:
        return _optional_text(value)

    @field_validator("reason")
    @classmethod
    def _require_reason(cls, value: str | None) -> str:
        if not value:
            raise ValueError("reason is required")
        return value

    @field_validator("missing_information", mode="before")
    @classmethod
    def _validate_missing_information(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("missing_information must be an array")
        return [
            item
            for item in (_optional_text(entry) for entry in value)
            if item is not None
        ]

    @field_validator("unsupported_claims", mode="before")
    @classmethod
    def _validate_unsupported_claims(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("unsupported_claims must be an array")
        return [
            item
            for item in (_optional_text(entry) for entry in value)
            if item is not None
        ]


_REFLECTION_RESPONSE_JSON_SCHEMA = ReflectionResponsePayload.model_json_schema()


def build_reflection_response_json_schema() -> dict[str, Any]:
    return _REFLECTION_RESPONSE_JSON_SCHEMA
