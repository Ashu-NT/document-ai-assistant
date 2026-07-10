from src.domain.extraction import ExtractedIdentifier, ExtractionResult

from .merge_support import best_confidence, normalize_for_dedup_key


def merge_identifiers(
    partial_results: list[ExtractionResult],
) -> list[ExtractedIdentifier]:
    merged: dict[tuple[str, str], ExtractedIdentifier] = {}
    for result in partial_results:
        for item in result.extracted_identifiers:
            key = (
                normalize_for_dedup_key(item.raw_value),
                normalize_for_dedup_key(item.identifier_type),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_identifier(merged[key], item)
    return list(merged.values())


def _merge_identifier(
    current: ExtractedIdentifier,
    candidate: ExtractedIdentifier,
) -> None:
    current.source_chunk_id = current.source_chunk_id or candidate.source_chunk_id
    current.confidence_score = best_confidence(
        current.confidence_score,
        candidate.confidence_score,
    )
    current.requires_human_review = (
        current.requires_human_review
        or candidate.requires_human_review
    )
