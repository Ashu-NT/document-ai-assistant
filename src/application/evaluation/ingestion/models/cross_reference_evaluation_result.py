from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CrossReferenceTypeMetrics:
    """P/R/F1 for one ChunkCrossReferenceType value within one case.

    `false_positives`/`precision` are `None` unless this type was declared
    exhaustively annotated for this case (via
    `IngestionExpectationCase.exhaustive_cross_reference_types`) - counting
    an unannotated actual reference as a false positive would punish the
    system for producing a reference nobody has reviewed yet, not for being
    wrong. Recall is always computable (it only depends on the curated
    expected list, never on the full actual set).
    """

    reference_type: str
    exhaustive: bool
    true_positives: int
    false_negatives: int
    false_positives: int | None
    matched_clues: tuple[str, ...] = ()
    missed_clues: tuple[str, ...] = ()

    @property
    def precision(self) -> float | None:
        if self.false_positives is None:
            return None
        denominator = self.true_positives + self.false_positives
        return (self.true_positives / denominator) if denominator else None

    @property
    def recall(self) -> float | None:
        denominator = self.true_positives + self.false_negatives
        return (self.true_positives / denominator) if denominator else None

    @property
    def f1(self) -> float | None:
        precision = self.precision
        recall = self.recall
        if precision is None or recall is None:
            return None
        if precision + recall == 0:
            return 0.0
        return 2 * precision * recall / (precision + recall)


@dataclass(slots=True)
class CrossReferenceEvaluationResult:
    case_id: str
    type_metrics: list[CrossReferenceTypeMetrics] = field(default_factory=list)
    # Counter(reconciliation_outcome.value) across every cross-reference in
    # the document graph, "(none)" for cross-references with no outcome set.
    reconciliation_outcome_counts: dict[str, int] = field(default_factory=dict)
    # "This clue must NOT resolve to an internal cross-reference" checks
    # (external standard/directive citations) - not scoped to a single
    # ChunkCrossReferenceType, so tracked separately from type_metrics.
    external_reference_clues_correctly_unresolved: int = 0
    external_reference_clues_incorrectly_resolved: int = 0


__all__ = ["CrossReferenceEvaluationResult", "CrossReferenceTypeMetrics"]
