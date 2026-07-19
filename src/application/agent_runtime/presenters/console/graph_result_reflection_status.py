from __future__ import annotations

from typing import Any

from src.application.langgraph.common import reflection_decision_from_state


def _reflection_reason(data: dict[str, Any]) -> str | None:
    reflection_result = data.get("reflection_result")
    if not isinstance(reflection_result, dict):
        return None
    decision = reflection_result.get("decision")
    if not isinstance(decision, dict):
        return None
    reason = decision.get("reason")
    if isinstance(reason, str) and reason.strip():
        return reason.strip()
    return None


def resolve_reflection_status(result) -> dict[str, str | None] | None:
    """Single source of truth for reflection visibility across every
    output surface -- console, JSON, Markdown, and both CLIs (finding F14,
    outputs/architecture/answering_and_prompt_fresh_audit.md: reflection
    visibility used to be computed one way for the console footer and a
    completely separate, flag-gated way in `agent_cli.py`).

    Returns `{"decision": ..., "reason": ...}` when reflection ran and
    produced a decision (`reason` may be `None`), `{"decision": None,
    "reason": "not active (self-check disabled)"}` when it's confirmed off
    for this turn, or `None` when there's no signal either way (e.g. a
    lightweight test double with no `diagnostics` at all)."""
    data = result.data or {}
    # getattr, not a direct attribute access: some lightweight result
    # doubles used elsewhere in this codebase's tests don't define
    # `diagnostics` at all.
    diagnostics = getattr(result, "diagnostics", None) or {}
    reflection = data.get("reflection_decision") or reflection_decision_from_state(data)
    if reflection:
        return {"decision": reflection, "reason": _reflection_reason(data)}
    if diagnostics.get("reflection_enabled") is False:
        # `reflection_enabled` is unconditionally set in
        # document_agent_result_builder.py's diagnostics dict from state,
        # so its being explicitly False (not just absent) is a clean,
        # already-surfaced signal that reflection never ran this turn at
        # all -- distinct from "reflection ran and had nothing to add"
        # (the branch above).
        return {"decision": None, "reason": "not active (self-check disabled)"}
    return None
