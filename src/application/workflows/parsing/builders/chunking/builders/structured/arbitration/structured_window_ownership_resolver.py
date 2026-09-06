from dataclasses import replace

from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration.structured_window_candidate import (
    StructuredWindowCandidate,
)


_UNANCHORED_DISTANCE = 2**31 - 1


class StructuredWindowOwnershipResolver:
    """Assigns shared structured context to one nearest evidence anchor."""

    def resolve(
        self,
        candidates: list[StructuredWindowCandidate],
    ) -> list[StructuredWindowCandidate]:
        if len(candidates) < 2:
            return candidates

        owners_by_element = self._owners_by_element(candidates)
        retained_ids = [set() for _ in candidates]
        for element_id, owner_indexes in owners_by_element.items():
            owner_index = self._select_owner(
                element_id=element_id,
                owner_indexes=owner_indexes,
                candidates=candidates,
            )
            retained_ids[owner_index].add(element_id)

        resolved = [
            replace(
                candidate,
                elements=tuple(
                    element
                    for element in candidate.elements
                    if element.element_id in retained_ids[index]
                ),
            )
            for index, candidate in enumerate(candidates)
            if retained_ids[index]
        ]
        return sorted(resolved, key=self._candidate_order)

    @staticmethod
    def _owners_by_element(
        candidates: list[StructuredWindowCandidate],
    ) -> dict[str, list[int]]:
        owners: dict[str, list[int]] = {}
        for index, candidate in enumerate(candidates):
            for element in candidate.elements:
                owners.setdefault(element.element_id, []).append(index)
        return owners

    def _select_owner(
        self,
        *,
        element_id: str,
        owner_indexes: list[int],
        candidates: list[StructuredWindowCandidate],
    ) -> int:
        if len(owner_indexes) == 1:
            return owner_indexes[0]

        anchor_owners = [
            index for index in owner_indexes if element_id in candidates[index].anchor_element_ids
        ]
        eligible = anchor_owners or owner_indexes
        element_order = self._element_order(element_id, candidates, owner_indexes)
        return min(
            eligible,
            key=lambda index: (
                self._anchor_distance(element_order, candidates[index]),
                -candidates[index].score,
                candidates[index].spec.chunk_type.value,
                candidates[index].order_index,
            ),
        )

    @staticmethod
    def _element_order(
        element_id: str,
        candidates: list[StructuredWindowCandidate],
        owner_indexes: list[int],
    ) -> int:
        for index in owner_indexes:
            for element in candidates[index].elements:
                if element.element_id == element_id:
                    return element.reading_order or 0
        return 0

    @staticmethod
    def _anchor_distance(
        element_order: int,
        candidate: StructuredWindowCandidate,
    ) -> int:
        anchor_orders = [
            element.reading_order or 0
            for element in candidate.elements
            if element.element_id in candidate.anchor_element_ids
        ]
        if not anchor_orders:
            return _UNANCHORED_DISTANCE
        return min(abs(element_order - anchor_order) for anchor_order in anchor_orders)

    @staticmethod
    def _candidate_order(candidate: StructuredWindowCandidate) -> tuple[int, str]:
        return candidate.order_index, candidate.spec.chunk_type.value
