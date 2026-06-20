from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)
from src.domain.common import ElementType
from src.domain.document import DocumentGraph
from src.domain.elements import CanonicalElement


class AssetNearbyTextEnricher:
    def __init__(
        self,
        *,
        context_window: int = 2,
        max_context_tokens: int = 72,
    ) -> None:
        self.context_window = max(0, context_window)
        self.max_context_tokens = max(12, max_context_tokens)

    def enrich(self, graph: DocumentGraph) -> None:
        if self.context_window <= 0:
            return

        for asset_collection, asset_kind in (
            (graph.tables, "table"),
            (graph.pictures, "picture"),
        ):
            for asset_id, asset in asset_collection.items():
                asset_element = self._find_asset_element(
                    graph=graph,
                    asset_id=asset_id,
                    asset_kind=asset_kind,
                )
                if asset_element is None or asset_element.parent_section_id is None:
                    continue

                section_elements = graph.get_section_elements(asset_element.parent_section_id)
                asset_index = self._find_element_index(
                    section_elements=section_elements,
                    asset_element=asset_element,
                )
                if asset_index is None:
                    continue

                asset.metadata.nearby_text = self._nearby_text(
                    section_elements=section_elements,
                    asset_index=asset_index,
                )

    def _nearby_text(
        self,
        *,
        section_elements: list[CanonicalElement],
        asset_index: int,
    ) -> str | None:
        asset_element = section_elements[asset_index]
        selected_parts: list[str] = []
        token_total = 0

        for candidate_index in range(
            max(0, asset_index - self.context_window),
            min(len(section_elements), asset_index + self.context_window + 1),
        ):
            if candidate_index == asset_index:
                continue

            candidate = section_elements[candidate_index]
            if not self._contributes_to_nearby_text(candidate):
                continue

            if not self._shares_page_context(asset_element, candidate):
                continue

            text = clean_chunk_text(candidate.text)
            if not text:
                continue

            remaining_tokens = self.max_context_tokens - token_total
            if remaining_tokens <= 0:
                break

            text = self._truncate_to_token_limit(text, remaining_tokens)
            if not text:
                continue

            selected_parts.append(text)
            token_total += len(text.split())

        if not selected_parts:
            return None

        return clean_chunk_text("\n\n".join(selected_parts))

    @staticmethod
    def _find_asset_element(
        *,
        graph: DocumentGraph,
        asset_id: str,
        asset_kind: str,
    ) -> CanonicalElement | None:
        for element in graph.elements.values():
            if asset_kind == "table" and element.table_id == asset_id:
                return element
            if asset_kind == "picture" and element.picture_id == asset_id:
                return element
        return None

    @staticmethod
    def _find_element_index(
        *,
        section_elements: list[CanonicalElement],
        asset_element: CanonicalElement,
    ) -> int | None:
        for index, candidate in enumerate(section_elements):
            if candidate.element_id == asset_element.element_id:
                return index
        return None

    @staticmethod
    def _contributes_to_nearby_text(element: CanonicalElement) -> bool:
        if element.element_type not in {
            ElementType.TEXT,
            ElementType.LIST_ITEM,
            ElementType.KEY_VALUE,
            ElementType.CODE,
        }:
            return False

        parser_extra = (
            element.parser_metadata.extra
            if element.parser_metadata is not None
            and element.parser_metadata.extra is not None
            else {}
        )
        parent_ref = parser_extra.get("parent_ref")
        if isinstance(parent_ref, str) and parent_ref.startswith("#/pictures/"):
            return False

        return parser_extra.get("content_layer") != "furniture"

    @staticmethod
    def _shares_page_context(
        asset_element: CanonicalElement,
        candidate: CanonicalElement,
    ) -> bool:
        asset_page = asset_element.source.page_start
        candidate_page = candidate.source.page_start
        if asset_page is None or candidate_page is None:
            return True
        return abs(candidate_page - asset_page) <= 1

    @staticmethod
    def _truncate_to_token_limit(text: str, max_tokens: int) -> str:
        tokens = text.split()
        if len(tokens) <= max_tokens:
            return text
        return " ".join(tokens[:max_tokens]).strip()
