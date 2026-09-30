"""Preserves the distinction YAML/dict key-presence already carries -
`normalize_expected_fields()` (used only for the diagnostic/content-
comparison path, never for identity) discards it by filling every content
field with `None`. This module is the single place that resolves a golden
expectation's RAW `expected_fields` mapping (only the keys a human actually
wrote down are present) into one of three states, so identity matching can
tell "not mentioned" apart from "explicitly asserted empty".
"""

from collections.abc import Mapping
from enum import StrEnum


class FieldAssertionState(StrEnum):
    NOT_ASSERTED = "not_asserted"
    EXPECTED_NULL = "expected_null"
    EXPECTED_VALUE = "expected_value"


def resolve_field_assertion(
    expected_fields: Mapping[str, str | None], field_name: str
) -> tuple[FieldAssertionState, str | None]:
    """`expected_fields` must be the RAW mapping as authored (only asserted
    keys present) - never the `normalize_expected_fields()`-filled dict,
    which has already collapsed NOT_ASSERTED and EXPECTED_NULL into the
    same `None` value for every content field."""
    if field_name not in expected_fields:
        return FieldAssertionState.NOT_ASSERTED, None
    value = expected_fields[field_name]
    if value is None:
        return FieldAssertionState.EXPECTED_NULL, None
    return FieldAssertionState.EXPECTED_VALUE, value


def is_asserted(expected_fields: Mapping[str, str | None], field_name: str) -> bool:
    return field_name in expected_fields


def effective_identity_fields(
    expected_fields: Mapping[str, str | None],
    identity_field_names: tuple[str, ...],
) -> tuple[str, ...]:
    """effective_identity_fields = production_identity_fields ∩
    fields_actually_asserted_by_this_expectation - a field this expectation
    never mentions is dropped from identity comparison entirely (never
    treated as "expected empty"); a field explicitly asserted as null
    (present in `expected_fields` with a `None` value) is KEPT and will
    assert emptiness."""
    return tuple(
        field_name
        for field_name in identity_field_names
        if is_asserted(expected_fields, field_name)
    )


def has_usable_identity_assertion(
    expected_fields: Mapping[str, str | None],
    identity_field_names: tuple[str, ...],
) -> bool:
    """A positive expectation needs at least one identity field asserted as
    an actual EXPECTED_VALUE (a real string) to avoid vacuously matching
    every candidate. EXPECTED_NULL alone does NOT count, even if it is the
    only asserted field: asserting emptiness is the absence of a positive
    fact to match against, not a specific claim about the entity, and for
    every one of the 12 production entity types there is no identity field
    where "the model produced nothing here, and nothing else was asserted
    either" is a meaningful, source-grounded golden claim. This is a
    deliberately conservative reading of "can this null assertion actually
    discriminate candidates" - see the Phase 2B pre-improvement
    investigation report for the audit across all 12 types."""
    return any(
        resolve_field_assertion(expected_fields, field_name)[0]
        is FieldAssertionState.EXPECTED_VALUE
        for field_name in identity_field_names
    )


__all__ = [
    "FieldAssertionState",
    "resolve_field_assertion",
    "is_asserted",
    "effective_identity_fields",
    "has_usable_identity_assertion",
]
