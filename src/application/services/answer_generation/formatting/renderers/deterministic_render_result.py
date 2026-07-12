from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DeterministicRenderResult:
    answer_text: str
    model_name: str
    renderer_name: str
    diagnostics: dict[str, object] = field(default_factory=dict)
