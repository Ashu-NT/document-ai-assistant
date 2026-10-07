from enum import StrEnum


class TableSemanticEvaluationOutcome(StrEnum):
    """Per-column comparison of classifier output against human-reviewed
    source truth. Deliberately NOT collapsed into one accuracy number --
    a false resolution (the classifier confidently names the wrong role)
    is a categorically different, more severe failure than an honest
    abstention on a knowable column, because a future deterministic-
    ownership mechanism would trust RESOLVED decisions.
    """

    CORRECT_RESOLUTION = "correct_resolution"
    """Classifier RESOLVED to exactly the human-mapped role."""

    FALSE_RESOLUTION = "false_resolution"
    """Classifier RESOLVED, but to the wrong role (human: KNOWN_MAPPED to a
    DIFFERENT role, or KNOWN_UNMAPPED/GENUINELY_AMBIGUOUS/UNKNOWN entirely).
    High severity -- see module docstring."""

    SAFE_ABSTENTION_AMBIGUOUS = "safe_abstention_ambiguous"
    """Classifier AMBIGUOUS where human truth is KNOWN_MAPPED (a knowable
    column) -- safe, but a coverage gap, not a correctness failure."""

    SAFE_ABSTENTION_UNKNOWN = "safe_abstention_unknown"
    """Classifier UNKNOWN where human truth is KNOWN_MAPPED (a knowable
    column) -- safe, but a coverage gap, not a correctness failure."""

    CORRECT_AMBIGUITY = "correct_ambiguity"
    """Classifier AMBIGUOUS where human source truth is itself
    GENUINELY_AMBIGUOUS -- the classifier correctly reflected real source
    ambiguity rather than forcing a guess."""

    CORRECT_UNKNOWN = "correct_unknown"
    """Classifier UNKNOWN where human truth is itself UNKNOWN -- the
    classifier correctly reflected that the source does not support any
    judgment."""

    KNOWN_UNMAPPED_HANDLING = "known_unmapped_handling"
    """Human truth is KNOWN_UNMAPPED (a real, understood concept with no
    role in the current vocabulary). Reported separately, never folded into
    the resolved-precision/coverage metrics, since there is no "correct"
    classifier role to compare against -- only whether the classifier
    avoided a false resolution (state recorded for transparency, not scored
    pass/fail)."""

    UNREVIEWED_OR_UNLOCATABLE = "unreviewed_or_unlocatable"
    """Not counted in any metric -- either the golden case was not yet
    human-reviewed (CANDIDATE), or the referenced real table could not be
    re-located in a fresh parse."""
