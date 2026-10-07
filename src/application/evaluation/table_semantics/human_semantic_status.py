from enum import StrEnum


class HumanSemanticStatus(StrEnum):
    """What a human reviewer, working from SOURCE evidence alone (header,
    neighboring headers, representative cell values, caption, section path,
    nearby text), could establish about one column's true meaning in its
    specific source table. This is independent of, and reviewed BEFORE
    looking at, any TableColumnSemanticClassifier output -- it describes
    source truth, never a classifier prediction.

    KNOWN_MAPPED        -- the reviewer understands the column's meaning,
                           and it corresponds to an existing
                           TableColumnSemanticRole (see `human_role`).
    KNOWN_UNMAPPED      -- the reviewer understands the column's meaning,
                           but no existing role fits it (see
                           `human_concept` for the human-readable concept).
    GENUINELY_AMBIGUOUS -- the SOURCE ITSELF does not provide enough
                           information to safely distinguish between two or
                           more plausible meanings (a property of the
                           source, not of the classifier's confidence).
    UNKNOWN             -- the reviewer cannot establish the column's
                           meaning from the evidence actually available.
    """

    KNOWN_MAPPED = "known_mapped"
    KNOWN_UNMAPPED = "known_unmapped"
    GENUINELY_AMBIGUOUS = "genuinely_ambiguous"
    UNKNOWN = "unknown"
