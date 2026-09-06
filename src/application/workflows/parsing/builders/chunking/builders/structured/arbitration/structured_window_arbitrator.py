from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration.structured_window_candidate import (
    StructuredWindowCandidate,
)


class StructuredWindowArbitrator:
    """Selects one semantic owner when candidate evidence materially conflicts."""

    def __init__(self, *, containment_threshold: float = 0.8, min_score_gap: int = 2) -> None:
        self.containment_threshold = containment_threshold
        self.min_score_gap = min_score_gap

    def select(
        self,
        candidates: list[StructuredWindowCandidate],
    ) -> list[StructuredWindowCandidate]:
        selected: list[StructuredWindowCandidate] = []
        for component in self._components(candidates):
            selected.extend(self._select_component(component))
        return sorted(selected, key=lambda candidate: candidate.order_index)

    def _select_component(
        self,
        candidates: list[StructuredWindowCandidate],
    ) -> list[StructuredWindowCandidate]:
        if len(candidates) == 1:
            return candidates

        ordered = sorted(
            candidates,
            key=lambda candidate: (
                -candidate.score,
                -int(candidate.direct_evidence),
                candidate.spec.chunk_type.value,
                candidate.order_index,
            ),
        )
        winner = ordered[0]
        runner_up = ordered[1]
        direct_candidates = [
            candidate for candidate in ordered if candidate.direct_evidence
        ]
        if len(direct_candidates) > 1:
            direct_components = self._components(direct_candidates)
            if len(direct_components) > 1:
                return [
                    selected
                    for component in direct_components
                    for selected in self._select_component(component)
                ]
        if winner.direct_evidence and not runner_up.direct_evidence:
            return [winner]
        if winner.score - runner_up.score >= self.min_score_gap:
            return [winner]
        if all(candidate.spec.chunk_type == winner.spec.chunk_type for candidate in ordered):
            return [winner]

        # Ambiguous competing labels are safer as ordinary GENERAL evidence.
        return []

    def _components(
        self,
        candidates: list[StructuredWindowCandidate],
    ) -> list[list[StructuredWindowCandidate]]:
        remaining = set(range(len(candidates)))
        components: list[list[StructuredWindowCandidate]] = []
        while remaining:
            seed = remaining.pop()
            component_indexes = {seed}
            frontier = [seed]
            while frontier:
                current = frontier.pop()
                neighbors = {
                    index
                    for index in remaining
                    if self._compete(candidates[current], candidates[index])
                }
                remaining.difference_update(neighbors)
                component_indexes.update(neighbors)
                frontier.extend(neighbors)
            components.append([candidates[index] for index in component_indexes])
        return components

    def _compete(
        self,
        left: StructuredWindowCandidate,
        right: StructuredWindowCandidate,
    ) -> bool:
        if left.anchor_element_ids & right.anchor_element_ids:
            return True
        left_ids = left.element_ids
        right_ids = right.element_ids
        smaller = min(len(left_ids), len(right_ids))
        if smaller == 0:
            return False
        containment = len(left_ids & right_ids) / smaller
        if containment < self.containment_threshold:
            return False
        if left.spec.chunk_type == right.spec.chunk_type:
            return True
        return not (
            left.direct_evidence
            and right.direct_evidence
            and left.anchor_element_ids.isdisjoint(right.anchor_element_ids)
        )
