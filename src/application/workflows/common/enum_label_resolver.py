from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import TypeVar

# Normalize-then-match enum-label resolution -- previously reimplemented
# independently in classification_shared.py::resolve_enum_label,
# extraction_workflow.py's `_resolve_contact_point_type` /
# `_resolve_contact_owner_type`, and inline in extraction_workflow.py's
# `_build_procedure` (`ProcedureType(...)` try/except). None of these were
# byte-identical: they differ in how the raw value is normalized, whether
# an alias table is consulted before falling back to direct enum
# construction, whether an already-resolved enum instance is accepted
# as-is, whether the resolved member is restricted to an allowed subset,
# and what "no match" falls back to. `resolve_enum_value` below is the
# single shared primitive; every call site passes only the knobs it
# actually needs so its exact existing behavior is preserved.

EnumT = TypeVar("EnumT", bound=Enum)


def resolve_enum_value(
    value: object,
    enum_cls: type[EnumT],
    *,
    normalize: Callable[[str], str],
    aliases: dict[str, EnumT] | None = None,
    match_member_name: bool = False,
    allowed_members: frozenset[EnumT] | None = None,
    default: EnumT | None,
) -> EnumT | None:
    """Resolves a raw value to a member of `enum_cls`.

    - If `value` is already an instance of `enum_cls`, it is returned
      as-is (subject to `allowed_members` filtering).
    - If `value` is `None`, `default` is returned directly (the raw value
      is never normalized/looked up).
    - Otherwise `value` is stringified and passed through `normalize`,
      then resolved via `aliases` (if given and it contains the
      normalized text), or by matching against each member's `.value`
      (and, if `match_member_name` is set, each member's lower-cased
      `.name` too), or -- if neither `aliases` nor `match_member_name`
      apply -- by constructing `enum_cls(normalized)` directly.
    - Whenever nothing matches, `default` is returned.
    - If `allowed_members` is given, a resolved member outside that set
      resolves to `None` (regardless of `default`), matching the two
      ExtractionWorkflow call sites that restrict `SemanticEntityType`
      resolution to a subset of members.
    """
    if isinstance(value, enum_cls):
        if allowed_members is not None and value not in allowed_members:
            return None
        return value

    if value is None:
        return default

    normalized = normalize(str(value))

    resolved: EnumT | None
    if aliases is not None and normalized in aliases:
        resolved = aliases[normalized]
    elif match_member_name:
        resolved = None
        for member in enum_cls:
            if normalized == member.value or normalized == member.name.lower():
                resolved = member
                break
        if resolved is None:
            return default
    else:
        try:
            resolved = enum_cls(normalized)
        except ValueError:
            return default

    if allowed_members is not None and resolved not in allowed_members:
        return None
    return resolved
