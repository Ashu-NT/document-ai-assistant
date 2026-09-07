from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CrossReferenceScope(StrEnum):
    """Whether a detected reference actually points within the current
    document. Detection alone (matching a phrase like "see section 6")
    never implies acceptance -- the same phrasing routinely shows up
    quoting or citing an external standard/directive/other manual."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    AMBIGUOUS = "ambiguous"


@dataclass(slots=True, frozen=True)
class CrossReferenceQualification:
    """The context-qualifier's verdict on one detected candidate. `reasons`
    is a short audit trail (e.g. "explicit_internal_lead_in",
    "external_anchor_present") -- always non-empty, so a qualification can
    be explained without re-deriving it."""

    scope: CrossReferenceScope
    confidence: float
    reasons: tuple[str, ...]


__all__ = ["CrossReferenceQualification", "CrossReferenceScope"]
