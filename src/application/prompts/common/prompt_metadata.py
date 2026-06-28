from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptMetadata:
    name: str
    version: str
    task_type: str
    model_type: str | None = None
    description: str | None = None
