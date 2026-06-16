from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ParserMetadata:
    parser_name: str
    parser_version: str | None = None
    raw_source_type: str | None = None
    raw_ref: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ModelProcessingMetadata:
    model_name: str
    model_type: str
    confidence: float | None = None
    prompt_version: str | None = None
    errors: list[str] = field(default_factory=list)
    