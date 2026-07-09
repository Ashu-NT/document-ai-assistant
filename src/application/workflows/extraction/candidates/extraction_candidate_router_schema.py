from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.application.prompts.extraction import ExtractionPromptType


class ExtractionCandidateRouterPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    candidate_types: list[str] = Field(default_factory=list)

    @field_validator("candidate_types", mode="before")
    @classmethod
    def _coerce_list(cls, value: Any) -> Any:
        if value is None:
            return []
        if not isinstance(value, list):
            return [value]
        return value

    def resolved_types(self) -> frozenset[ExtractionPromptType]:
        resolved: set[ExtractionPromptType] = set()
        for raw in self.candidate_types:
            normalized = (
                str(raw).strip().lower().replace(" ", "_").replace("-", "_")
            )
            try:
                resolved.add(ExtractionPromptType(normalized))
            except ValueError:
                continue
        return frozenset(resolved)


_EXTRACTION_CANDIDATE_ROUTER_JSON_SCHEMA = (
    ExtractionCandidateRouterPayload.model_json_schema()
)


def build_extraction_candidate_router_json_schema() -> dict[str, Any]:
    return _EXTRACTION_CANDIDATE_ROUTER_JSON_SCHEMA
