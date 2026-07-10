from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from src.application.workflows.common import coerce_confidence_score


def coerce_raw_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("list fields must be arrays")
    return value


class _ExtractionItemBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    @field_validator("confidence_score", mode="before", check_fields=False)
    @classmethod
    def _validate_confidence_score(cls, value: Any) -> Any:
        return coerce_confidence_score(
            value,
            normalize_percent_range=True,
            on_invalid="original",
        )
