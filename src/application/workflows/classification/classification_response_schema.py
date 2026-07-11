from __future__ import annotations

import re
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from src.application.workflows.common.confidence_coercion import coerce_confidence_score

_LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*]+|\d+[\.\)]|[A-Za-z]\))\s*")


def _coerce_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().strip('"').strip("'").split())
    return text or None


def _coerce_evidence_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = [value]
    evidence: list[str] = []
    for item in items:
        text = _coerce_text(item)
        if not text:
            continue
        normalized = _LIST_ITEM_PATTERN.sub("", text).strip()
        if normalized:
            evidence.append(normalized)
    return evidence


class ClassificationResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    label: str = Field(
        validation_alias=AliasChoices(
            "label",
            "predicted_label",
            "document_type",
            "chunk_type",
        )
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("confidence_score", "confidence", "score")
    )
    rationale: str | None = None
    evidence: list[str] = Field(default_factory=list)

    @field_validator("label", "rationale", mode="before")
    @classmethod
    def _validate_text(cls, value: Any) -> Any:
        return _coerce_text(value)

    @field_validator("label")
    @classmethod
    def _require_label(cls, value: str | None) -> str:
        if not value:
            raise ValueError("label is required")
        return value

    @field_validator("confidence_score", mode="before")
    @classmethod
    def _validate_confidence_score(cls, value: Any) -> Any:
        return coerce_confidence_score(
            value,
            coerce_numeric_input=False,
            parse_unmarked_numeric_strings=False,
            on_invalid="original",
        )

    @field_validator("evidence", mode="before")
    @classmethod
    def _validate_evidence(cls, value: Any) -> Any:
        return _coerce_evidence_items(value)


_CLASSIFICATION_RESPONSE_JSON_SCHEMA = ClassificationResponsePayload.model_json_schema()


def build_classification_response_json_schema() -> dict[str, Any]:
    return _CLASSIFICATION_RESPONSE_JSON_SCHEMA
