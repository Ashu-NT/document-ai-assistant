"""Single source of truth for plan-tool naming/argument constants.

``plan_validator.py`` and ``plan_repair.py`` each grew their own copy of the
tool-arg allow-list, and ``plan_repair.py`` additionally owns the only
tool-rename map. The allow-lists (``KNOWN_TOOL_ARGS`` below) were identical
dict literals in both files, so they are merged here verbatim.

The two files' "which tool names are risky" marker lists had drifted apart
instead: ``plan_validator.py`` used a 5-marker list to decide whether a step
*looks* mutating (only enforced when the policy disallows mutating tools),
while ``plan_repair.py`` used a different, 3-marker list to hard-fail
repair of a *required* step outright (enforced unconditionally). These are
genuinely different checks with different marker sets, not one drifted copy
of the other, so both are kept here as distinct, separately named constants
rather than force-merged into one list.
"""

from __future__ import annotations

# Tool-arg allow-list, formerly duplicated verbatim as
# `plan_validator.py::_KNOWN_ARGS` and `plan_repair.py::_ALLOWED_ARGS`.
KNOWN_TOOL_ARGS: dict[str, set[str]] = {
    "list_documents": set(),
    "find_document": {"document_id", "query_text", "query"},
    "document_details": {"document_id"},
    "explore_document": {"document_id"},
    "retrieve_chunks": {"document_id", "query_text", "question", "top_k", "chunk_types"},
    "retrieve_identifiers": {"identifier_value", "identifier_type", "document_id", "query"},
    "retrieve_structured_entities": {"entity_type", "document_id", "query_text", "top_k"},
    "answer_question": {"document_id", "question", "top_k"},
    "run_quality_gate": {"report_path", "thresholds_path"},
    "retrieval_trace": {"document_id", "query_text", "top_k", "write_output"},
}

# Formerly `plan_repair.py::_TOOL_NAME_RENAMES`.
TOOL_NAME_RENAMES: dict[str, str] = {
    "retrieve_evidence": "retrieve_chunks",
    "ask_question": "answer_question",
    "lookup_document": "find_document",
}

# Formerly `plan_validator.py::_MUTATING_TOOL_MARKERS`. Used by
# `PlanValidator._looks_mutating` to flag a step as an error only when the
# active policy disallows mutating tools.
MUTATING_TOOL_MARKERS: tuple[str, ...] = (
    "ingest",
    "delete",
    "reingest",
    "remove",
    "replace",
)

# Formerly the inline tuple in `plan_repair.py::PlanRepair.repair`. Used to
# refuse to repair a plan at all when a *required* step's tool name matches
# one of these markers, unconditionally (no policy gate).
REPAIR_UNSAFE_REQUIRED_STEP_MARKERS: tuple[str, ...] = (
    "delete",
    "ingest",
    "reingest",
)
