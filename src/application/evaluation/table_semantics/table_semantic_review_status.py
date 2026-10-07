from enum import StrEnum


class TableSemanticReviewStatus(StrEnum):
    """Same lifecycle convention already established for classification
    expectations (see ClassificationReviewStatus): every golden column
    entry starts as CANDIDATE; only an entry a human explicitly marked
    REVIEWED (source-supported, independent of classifier output) may be
    counted in authoritative evaluation metrics. A separate enum, not an
    import of ClassificationReviewStatus, to avoid coupling this
    table-semantics evaluation package to the unrelated classification
    evaluation package -- the convention is reused, not the class.
    """

    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
