from abc import ABC, abstractmethod

from src.application.workflows.parsing.canonical_element import CanonicalElement


class SectionHierarchyStrategy(ABC):
    name: str

    @abstractmethod
    def can_apply(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def assign_levels(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> dict[str, int]:
        raise NotImplementedError
