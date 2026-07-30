from abc import ABC, abstractmethod

from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement


class SectionHierarchyStrategy(ABC):
    name: str

    @abstractmethod
    def can_apply(
        self,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def assign_levels(
        self,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> dict[str, int]:
        raise NotImplementedError
