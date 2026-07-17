import json


def split_section_path(parts: list[str]) -> tuple[list[str], list[str]]:
    if len(parts) <= 2:
        return parts, []
    return parts[-2:], parts[:-2]


def ordered_query_match(*, normalized_combined: str, query_terms: list[str]) -> float:
    if len(query_terms) < 2:
        return 0.0

    haystack_tokens = normalized_combined.split()
    query_index = 0
    matched_positions: list[int] = []

    for index, token in enumerate(haystack_tokens):
        if token != query_terms[query_index]:
            continue
        matched_positions.append(index)
        query_index += 1
        if query_index == len(query_terms):
            break

    if query_index < 2:
        return 0.0
    if query_index == len(query_terms):
        span = matched_positions[-1] - matched_positions[0] + 1
        return 10.0 if span <= max(8, len(query_terms) * 2) else 7.0
    return float(query_index) * 1.5


def looks_like_toc_content(content: str) -> bool:
    lowered = (content or "").lower()
    return (
        "...." in lowered
        or ("table of contents" in lowered)
        or (".." in lowered and any(char.isdigit() for char in lowered))
    )


def section_path_parts(raw_section_path: str | None) -> list[str]:
    if not raw_section_path:
        return []
    try:
        loaded = json.loads(raw_section_path)
    except json.JSONDecodeError:
        return []
    if not isinstance(loaded, list):
        return []
    return [str(part) for part in loaded if str(part).strip()]
