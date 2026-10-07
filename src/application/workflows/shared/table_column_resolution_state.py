from enum import StrEnum


class ColumnResolutionState(StrEnum):
    """Non-overlapping outcome of resolving one column's semantic role.

    RESOLVED  -- one existing SemanticRole has sufficient, sufficiently
                 separated evidence.
    AMBIGUOUS -- two or more existing SemanticRole candidates have
                 meaningful, competing support and cannot be safely
                 distinguished. This is a STATE, never itself a semantic
                 role.
    UNKNOWN   -- the classifier cannot establish what the column
                 semantically represents with sufficient confidence. This
                 covers zero evidence, weak/below-threshold evidence for a
                 known role, AND conflicting evidence that never forms a
                 genuinely plausible candidate set. A column can have
                 evidence items and still be UNKNOWN -- weak support for a
                 role is not the same as an understood-but-unmapped
                 concept (see UNMAPPED).
    UNMAPPED  -- the classifier has AFFIRMATIVE evidence that the column
                 represents a coherent semantic concept, but that concept
                 intentionally has no slot in the current SemanticRole
                 vocabulary. This requires a positive, generic judgment of
                 "this is some coherent thing" independent of role
                 scoring -- NOT merely "some weak evidence existed but
                 nothing resolved" (that is UNKNOWN). No implementation is
                 required to ever reach this state; it is acceptable, and
                 preferable to inventing heuristics, for it to stay
                 unreachable until a classifier actually has machinery
                 capable of that distinct judgment.
    """

    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"
    UNMAPPED = "unmapped"
