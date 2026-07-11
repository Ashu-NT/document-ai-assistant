from __future__ import annotations

from typing import Any


def format_action_steps(trace_entries: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    seen: set[tuple[str, str]] = set()
    for entry in trace_entries:
        if not isinstance(entry, dict):
            continue
        tool_name = str(entry.get("tool_name") or "").strip()
        if not tool_name:
            continue
        node_name = str(entry.get("node_name") or "").strip() or tool_name
        key = (node_name, tool_name)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"Tool: {tool_name}")
        lines.append(f"Purpose: {_tool_purpose(tool_name)}")
        lines.append("")
    return "\n".join(lines).strip()


def _tool_purpose(tool_name: str) -> str:
    purposes = {
        "retrieve_chunks": "collect document-scoped evidence.",
        "retrieve_tables": "collect structured table evidence.",
        "retrieve_identifiers": "collect identifier-level evidence.",
        "retrieve_figures": "collect figure-adjacent evidence.",
        "answer_question": "generate a grounded answer from validated evidence.",
        "find_document": "resolve the requested document in the corpus.",
        "list_documents": "list available documents in the corpus.",
    }
    return purposes.get(tool_name, "execute a validated application action.")
