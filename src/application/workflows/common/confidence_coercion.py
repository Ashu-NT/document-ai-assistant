from __future__ import annotations

from typing import Any, Literal

# Confidence-score coercion (numeric / percent-string parsing) --
# previously reimplemented three times (extraction_workflow.py's
# `_parse_confidence`, extraction_response_schema.py's `_coerce_confidence`,
# classification_response_schema.py's `_coerce_confidence`) with genuinely
# different edge-case behavior at each site rather than being byte-
# identical copies:
#
# - whether a numeric (or bool) input is coerced/normalized at all
#   (extraction_workflow, extraction_response_schema) or returned
#   completely unchanged (classification_response_schema, which only ever
#   coerces percent-suffixed strings and passes every other input through
#   untouched);
# - whether a bool input is treated as a number (extraction_workflow) or
#   returned unchanged (extraction_response_schema, which runs as a
#   pydantic "before" validator and lets pydantic's own bool/float
#   coercion -- or rejection -- happen downstream);
# - whether a plain numeric value/string outside 0-1 but inside
#   (1, 100] is reinterpreted as a percentage and divided by 100
#   (extraction_response_schema only);
# - whether a string without a trailing "%" is still parsed as a plain
#   float (extraction_workflow, extraction_response_schema) or left
#   untouched (classification_response_schema);
# - what is returned when parsing fails: `None` (extraction_workflow,
#   which uses the result directly as `confidence_score`) or the original,
#   un-coerced value (the two schema validators, so pydantic's own field
#   validation reports the error instead of silently defaulting);
# - whether a non-string, non-numeric value (e.g. a list/dict, however
#   unlikely) is still stringified and run through the same percent/float
#   parsing (extraction_workflow's `str(value)` runs unconditionally once
#   the None/int/float checks fall through) or left completely untouched
#   (the two schema validators, gated on `isinstance(value, str)`).
#
# The knobs below let every call site keep its exact existing behavior.

_OnInvalid = Literal["none", "original"]


def coerce_confidence_score(
    value: Any,
    *,
    coerce_numeric_input: bool = True,
    treat_bool_as_number: bool = False,
    normalize_percent_range: bool = False,
    parse_unmarked_numeric_strings: bool = True,
    stringify_non_string_values: bool = False,
    on_invalid: _OnInvalid = "none",
) -> Any:
    invalid_result = None if on_invalid == "none" else value

    if coerce_numeric_input:
        if isinstance(value, bool) and not treat_bool_as_number:
            return value

        if isinstance(value, (int, float)):
            numeric = float(value)
            if normalize_percent_range and 1 < numeric <= 100:
                return numeric / 100
            return numeric

    if isinstance(value, str) or stringify_non_string_values:
        stripped = str(value).strip().strip('"').strip("'").strip()
        if stripped.endswith("%"):
            try:
                return float(stripped[:-1].strip()) / 100
            except ValueError:
                return invalid_result

        if not parse_unmarked_numeric_strings:
            return value

        if not stripped:
            return invalid_result

        try:
            numeric = float(stripped)
        except ValueError:
            return invalid_result

        if normalize_percent_range and 1 < numeric <= 100:
            return numeric / 100
        return numeric

    return value
