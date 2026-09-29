from enum import StrEnum


class ExtractionCompleteness(StrEnum):
    """Mirrors the existing exhaustive/non-exhaustive idiom already used for
    cross-reference metrics (`IngestionExpectationCase.
    exhaustive_cross_reference_types`), generalized to extraction.

    - PRESENCE_ONLY: the annotated expectations are known-expected entities;
      additional extracted entities are NOT automatically false positives
      (they may simply be unreviewed). Only TP/FN/Recall are meaningful.
    - EXHAUSTIVE: the annotated scope has been comprehensively reviewed;
      any unmatched extracted entity within that scope is a real false
      positive. TP/FP/FN/Precision/Recall/F1 are all meaningful.

    Never inferred from fixture shape (e.g. "has multiple expectations") -
    always an explicit, human-authored declaration.
    """

    PRESENCE_ONLY = "presence_only"
    EXHAUSTIVE = "exhaustive"
