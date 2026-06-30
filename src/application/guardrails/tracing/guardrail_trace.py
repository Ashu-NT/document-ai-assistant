from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.application.guardrails.models.guardrail_result import GuardrailResult


def _serialize_trace_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {
            str(key): _serialize_trace_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple | set | frozenset):
        return [_serialize_trace_value(item) for item in value]
    return value


@dataclass(slots=True, frozen=True)
class GuardrailTraceEntry:
    layer: str
    decision: str
    severity: str
    policy: str
    violation_type: str | None = None
    matched_terms: list[str] = field(default_factory=list)
    route: str | None = None
    blocked_tool: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(slots=True)
class GuardrailTrace:
    trace_id: str = field(default_factory=lambda: uuid4().hex)
    entries: list[GuardrailTraceEntry] = field(default_factory=list)

    def append(
        self,
        *,
        layer: str,
        policy: str,
        result: GuardrailResult,
        route: str | None = None,
        blocked_tool: str | None = None,
    ) -> GuardrailResult:
        violation = result.violations[0] if result.violations else None
        self.entries.append(
            GuardrailTraceEntry(
                layer=layer,
                decision=result.decision.value,
                severity=result.severity.value,
                policy=policy,
                violation_type=(
                    str(violation.violation_type) if violation is not None else None
                ),
                matched_terms=list(getattr(violation, "matched_terms", []) or []),
                route=route,
                blocked_tool=blocked_tool,
            )
        )
        result.trace_id = self.trace_id
        result.diagnostics.setdefault("guardrail_trace_id", self.trace_id)
        result.diagnostics["guardrail_trace"] = self.to_dict()["entries"]
        return result

    def to_dict(self) -> dict[str, Any]:
        return _serialize_trace_value(
            {
                "trace_id": self.trace_id,
                "entries": [asdict(entry) for entry in self.entries],
            }
        )
