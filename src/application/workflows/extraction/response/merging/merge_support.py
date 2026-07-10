from src.domain.common import SourceLocation


def normalize_for_dedup_key(value: str | None) -> str:
    if value is None:
        return ""
    normalized = "".join(
        character.lower()
        for character in value.strip()
        if character.isalnum()
    )
    return normalized


def best_confidence(
    left: float | None,
    right: float | None,
) -> float | None:
    if left is None:
        return right
    if right is None:
        return left
    return max(left, right)


def is_empty_source(source: SourceLocation) -> bool:
    return source.page_start is None and source.page_end is None and source.bbox is None


def merge_common_fields(current, candidate) -> None:
    current.source_chunk_id = current.source_chunk_id or candidate.source_chunk_id
    current.confidence_score = best_confidence(
        current.confidence_score,
        candidate.confidence_score,
    )
    current.requires_human_review = (
        current.requires_human_review
        or candidate.requires_human_review
    )
    if is_empty_source(current.source) and not is_empty_source(candidate.source):
        current.source = SourceLocation(
            page_start=candidate.source.page_start,
            page_end=candidate.source.page_end,
            bbox=candidate.source.bbox,
        )
