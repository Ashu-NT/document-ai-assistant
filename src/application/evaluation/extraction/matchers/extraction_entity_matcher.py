"""Deterministic entity matcher. Never uses an LLM judge - primary matching
is production identity/dedup semantics (`entity_identity_keys.py`) then
deterministic field comparison (`field_match_modes.py`)."""

from collections.abc import Sequence
from dataclasses import dataclass

from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractionExpectationCase,
)
from src.application.evaluation.extraction.extraction_field_extraction import (
    content_field_names,
    normalize_expected_fields,
)
from src.application.evaluation.extraction.matchers.entity_identity_keys import (
    ENTITY_IDENTITY_FIELD_NAMES,
    compute_identity_key,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
    ExtractionMatchResult,
)
from src.application.evaluation.extraction.matchers.field_match_modes import (
    FieldMatchMode,
    match_mode_for_field,
)
from src.application.workflows.extraction.response.merging.merge_support import (
    normalize_for_dedup_key as _norm,
)


@dataclass(frozen=True, slots=True)
class _ActualEntity:
    entity_id: str
    fields: dict[str, str | None]


def _fields_match(
    expected_value: str | None,
    actual_value: str | None,
    *,
    mode: FieldMatchMode,
) -> bool:
    normalized_expected = _norm(expected_value)
    normalized_actual = _norm(actual_value)
    if not normalized_expected and not normalized_actual:
        return True
    if normalized_expected == normalized_actual:
        return True
    if mode is FieldMatchMode.CONTAINS and normalized_expected:
        return normalized_expected in normalized_actual
    return False


def _identity_matches(
    expectation: ExtractionExpectationCase,
    expected_fields: dict[str, str | None],
    actual: _ActualEntity,
) -> bool:
    identity_field_names = expectation.identity_fields_override or (
        ENTITY_IDENTITY_FIELD_NAMES[expectation.entity_type]
    )
    for field_name in identity_field_names:
        mode = match_mode_for_field(expectation.entity_type, field_name)
        if not _fields_match(
            expected_fields.get(field_name),
            actual.fields.get(field_name),
            mode=mode,
        ):
            return False
    return True


def match_expectations_against_actuals(
    entity_type_value: str,
    expectations: Sequence[ExtractionExpectationCase],
    actual_entities: Sequence[_ActualEntity],
) -> list[ExtractionMatchResult]:
    """Matches every expectation against the full candidate list of actual
    entities (of the same entity type). Callers are responsible for scope
    filtering used for EXHAUSTIVE false-positive detection (see
    `golden_extraction_metrics.py`) - this function only performs entity
    identity matching, never scope/evidence filtering, since a
    content-correct entity outside the expected page range is still a
    content match (evidence correctness is scored separately).
    """
    results: list[ExtractionMatchResult] = []
    matched_actual_ids: set[str] = set()

    for expectation in expectations:
        entity_type = expectation.entity_type
        expected_fields = normalize_expected_fields(
            expectation.expected_fields, entity_type
        )
        identity_field_names = expectation.identity_fields_override or (
            ENTITY_IDENTITY_FIELD_NAMES[entity_type]
        )

        candidates = [
            actual
            for actual in actual_entities
            if _identity_matches(expectation, expected_fields, actual)
        ]

        if not candidates:
            results.append(
                ExtractionMatchResult(
                    outcome=ExtractionMatchOutcome.UNMATCHED_EXPECTED,
                    entity_type=entity_type.value,
                    group_completeness=expectation.completeness,
                    group_review_status=expectation.review_status,
                    expectation=expectation,
                    identity_fields_used=identity_field_names,
                    normalized_expected=expected_fields,
                    match_reason="no actual entity matched identity fields",
                )
            )
            continue

        if len(candidates) > 1:
            results.append(
                ExtractionMatchResult(
                    outcome=ExtractionMatchOutcome.UNMATCHED_EXPECTED,
                    entity_type=entity_type.value,
                    group_completeness=expectation.completeness,
                    group_review_status=expectation.review_status,
                    expectation=expectation,
                    identity_fields_used=identity_field_names,
                    normalized_expected=expected_fields,
                    match_reason=(
                        "ambiguous: multiple actual entities equally match "
                        "identity fields - not silently resolved"
                    ),
                    ambiguous_actual_entity_ids=tuple(
                        candidate.entity_id for candidate in candidates
                    ),
                )
            )
            continue

        actual = candidates[0]
        matched_actual_ids.add(actual.entity_id)
        differing_fields = tuple(
            field_name
            for field_name in content_field_names(entity_type)
            if not _fields_match(
                expected_fields.get(field_name),
                actual.fields.get(field_name),
                mode=match_mode_for_field(entity_type, field_name),
            )
        )
        results.append(
            ExtractionMatchResult(
                outcome=ExtractionMatchOutcome.MATCHED,
                entity_type=entity_type.value,
                group_completeness=expectation.completeness,
                group_review_status=expectation.review_status,
                expectation=expectation,
                actual_entity_id=actual.entity_id,
                identity_fields_used=identity_field_names,
                differing_fields=differing_fields,
                normalized_expected=expected_fields,
                normalized_actual=actual.fields,
                match_reason="identity fields matched",
            )
        )

    unmatched_actuals = [
        actual for actual in actual_entities if actual.entity_id not in matched_actual_ids
    ]
    # Every expectation in one call is required (by fixture-authoring
    # convention) to share one completeness/review_status per (document,
    # entity_type, scope) - taken from the first expectation, since
    # `entity_type_value`'s group is only ever invoked with a non-empty
    # `expectations` list (see golden_extraction_runner.py).
    group_completeness = (
        expectations[0].completeness
        if expectations
        else ExtractionMatchResult.__dataclass_fields__["group_completeness"].default
    )
    group_review_status = (
        expectations[0].review_status
        if expectations
        else ExtractionMatchResult.__dataclass_fields__["group_review_status"].default
    )
    for actual in unmatched_actuals:
        results.append(
            ExtractionMatchResult(
                outcome=ExtractionMatchOutcome.UNMATCHED_ACTUAL,
                entity_type=entity_type_value,
                group_completeness=group_completeness,
                group_review_status=group_review_status,
                actual_entity_id=actual.entity_id,
                normalized_actual=actual.fields,
                match_reason="no expectation matched this actual entity",
            )
        )

    return results


__all__ = ["_ActualEntity", "match_expectations_against_actuals"]
