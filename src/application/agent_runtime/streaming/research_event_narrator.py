from __future__ import annotations

from typing import Any


def build_evaluate_payload(state: dict[str, Any]) -> dict[str, Any]:
    research_trace = state.get("research_trace") or {}
    coverage = (
        research_trace.get("strategy_coverage") or {}
        if isinstance(research_trace, dict)
        else {}
    )
    ratio = coverage.get("ratio") if isinstance(coverage, dict) else None
    uncovered = coverage.get("uncovered_concepts") or [] if isinstance(coverage, dict) else []
    pending = bool(state.get("research_followup_pending"))

    parts: list[str] = []
    if ratio is not None:
        parts.append(f"Coverage: {float(ratio):.0%}")
    if uncovered:
        concepts = ", ".join(str(c) for c in uncovered[:3])
        parts.append(f"gap: {concepts}")
    if pending:
        parts.append("running follow-up retrieval")
    else:
        parts.append("moving to synthesis")

    detail = " — ".join(parts) if parts else "Evaluation complete."
    return {"kind": "evaluate", "detail": detail}
