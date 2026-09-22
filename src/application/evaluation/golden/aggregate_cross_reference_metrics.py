from dataclasses import dataclass

from src.application.evaluation.ingestion.models.cross_reference_evaluation_result import (
    CrossReferenceTypeMetrics,
)


@dataclass(slots=True, frozen=True)
class AggregateCrossReferenceTypeMetrics:
    """One ChunkCrossReferenceType's metrics summed across every document
    outcome that reported them this run.

    `true_positives`/`false_negatives` (and therefore recall) are summed
    across every contributing document regardless of annotation scope -
    recall only ever depends on the curated expected list. `false_positives`
    (and therefore precision) is summed ONLY from documents that declared
    this type exhaustively annotated for them - see
    CrossReferenceTypeMetrics's own docstring for why mixing in a
    presence-only document's unreviewed actual references would be wrong.
    """

    reference_type: str
    true_positives: int
    false_negatives: int
    false_positives: int | None
    exhaustive_document_count: int
    non_exhaustive_document_count: int

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


def aggregate_cross_reference_type_metrics(
    all_type_metrics: list[CrossReferenceTypeMetrics],
) -> list[AggregateCrossReferenceTypeMetrics]:
    by_type: dict[str, list[CrossReferenceTypeMetrics]] = {}
    for metrics in all_type_metrics:
        by_type.setdefault(metrics.reference_type, []).append(metrics)

    aggregates: list[AggregateCrossReferenceTypeMetrics] = []
    for reference_type in sorted(by_type):
        entries = by_type[reference_type]
        exhaustive_entries = [entry for entry in entries if entry.exhaustive]
        aggregates.append(
            AggregateCrossReferenceTypeMetrics(
                reference_type=reference_type,
                true_positives=sum(entry.true_positives for entry in entries),
                false_negatives=sum(entry.false_negatives for entry in entries),
                false_positives=(
                    sum(entry.false_positives or 0 for entry in exhaustive_entries)
                    if exhaustive_entries
                    else None
                ),
                exhaustive_document_count=len(exhaustive_entries),
                non_exhaustive_document_count=len(entries) - len(exhaustive_entries),
            )
        )
    return aggregates


__all__ = [
    "AggregateCrossReferenceTypeMetrics",
    "aggregate_cross_reference_type_metrics",
]
