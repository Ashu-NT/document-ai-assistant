from __future__ import annotations

_COMPOUND_MARKERS = (
    " and ",
    " compare ",
    " then ",
    " also ",
    "summarize evidence",
    "retrieve evidence",
)
_TASK_KEYWORDS = (
    "explore",
    "retrieve",
    "evidence",
    "summarize",
    "compare",
    "specification",
    "maintenance",
    "safety",
    "procedure",
    "sections",
    "tables",
)


def looks_compound(normalized_input: str) -> bool:
    if any(marker in f" {normalized_input} " for marker in _COMPOUND_MARKERS):
        return True
    keyword_hits = sum(
        1 for keyword in _TASK_KEYWORDS if keyword in normalized_input
    )
    return keyword_hits >= 2 and " and " in f" {normalized_input} "


def is_explore_and_answer_request(normalized_input: str) -> bool:
    return "explore" in normalized_input and any(
        marker in normalized_input
        for marker in ("list ", "summarize", "maintenance", "specification", "safety")
    )


def is_retrieve_and_answer_request(normalized_input: str) -> bool:
    return any(
        marker in normalized_input
        for marker in ("retrieve evidence", "show context", "summarize evidence")
    ) and any(marker in normalized_input for marker in ("summarize", "answer", "it"))


def is_compare_request(normalized_input: str) -> bool:
    return "compare" in normalized_input and " and " in normalized_input


def is_list_and_find_request(normalized_input: str) -> bool:
    return "show documents" in normalized_input and any(
        marker in normalized_input for marker in ("open ", "find ", "open document")
    )
