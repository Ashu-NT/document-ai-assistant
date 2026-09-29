from enum import StrEnum


class ExtractionApplicability(StrEnum):
    """First-class per-(document, entity_type, scope) applicability state.

    These three values are never collapsed into each other:
    - APPLICABLE: the entity type is within evaluation scope for this
      document/scope - absence of expected entities here is a real
      candidate for recall scoring, not a shrug.
    - NOT_APPLICABLE: source evidence establishes the entity type does not
      apply (e.g. MTU Part 1 defers MaintenanceInterval to a separate
      publication). This is NOT a false negative, and is NOT automatically
      a true negative either - it is simply excluded from FN/TN scoring.
    - NOT_ASSESSED: no truth judgment has been made yet. Contributes
      nothing to any metric. This is the default for any entity type no
      human/candidate annotation has touched - absence of annotation must
      never silently become "expected zero".
    """

    APPLICABLE = "applicable"
    NOT_APPLICABLE = "not_applicable"
    NOT_ASSESSED = "not_assessed"
