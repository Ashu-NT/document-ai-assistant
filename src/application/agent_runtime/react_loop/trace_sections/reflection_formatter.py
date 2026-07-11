from __future__ import annotations

from typing import Any


def format_reflection(data: dict[str, Any]) -> str:
    reflection_result = data.get("reflection_result")
    if not isinstance(reflection_result, dict):
        research_trace = data.get("research_trace")
        if not isinstance(research_trace, dict):
            return ""
        strategy_coverage = research_trace.get("strategy_coverage")
        if not isinstance(strategy_coverage, dict):
            return ""
        ratio = strategy_coverage.get("ratio")
        covered = strategy_coverage.get("covered_concepts", [])
        uncovered = strategy_coverage.get("uncovered_concepts", [])
        passed = bool(strategy_coverage.get("passed", False))
        lines = [
            f"Decision: {'PASS' if passed else 'REPLAN_REQUIRED'}",
        ]
        if isinstance(ratio, int | float):
            lines.append(f"Concept coverage: {float(ratio):.0%}")
        if covered:
            lines.append(
                "Covered concepts: " + ", ".join(str(item) for item in covered)
            )
        if uncovered:
            lines.append(
                "Uncovered concepts: " + ", ".join(str(item) for item in uncovered)
            )
        return "\n".join(lines)
    decision = (reflection_result.get("decision") or {}).get("decision") or data.get(
        "reflection_decision"
    )
    reason = (reflection_result.get("decision") or {}).get("reason")
    lines = [f"Decision: {decision or '-'}"]
    if data.get("reflection_score") is not None:
        lines.append(f"Overall score: {data.get('reflection_score')}")
    if reason:
        lines.append(f"Reason: {reason}")
    return "\n".join(lines)
