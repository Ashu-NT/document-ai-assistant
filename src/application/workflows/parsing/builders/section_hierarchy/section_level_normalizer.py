from src.application.workflows.parsing.canonical_element import CanonicalElement


def levels_are_weak(levels: dict[str, int]) -> bool:
    if not levels:
        return True

    return len(set(levels.values())) <= 1


def normalize_levels(
    headers: list[CanonicalElement],
    levels: dict[str, int],
) -> dict[str, int]:
    if not levels:
        return {}

    clamped = {
        header_id: min(max(level, 1), 6)
        for header_id, level in levels.items()
    }
    unique_levels = sorted(set(clamped.values()))
    normalized_levels = {
        original_level: index + 1
        for index, original_level in enumerate(unique_levels)
    }

    normalized = {
        header_id: normalized_levels[level]
        for header_id, level in clamped.items()
    }

    first_header_id = headers[0].element_id
    normalized[first_header_id] = 1
    return normalized
