from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)
from src.application.workflows.parsing.profiling import GraphBuildProfiler
from src.domain.common import ElementType
from src.domain.document import DocumentGraph
from src.domain.elements import CanonicalElement


class AssetNearbyTextEnricher:
    def __init__(
        self,
        *,
        context_window: int = 2,
        max_context_tokens: int = 72,
        profiler: GraphBuildProfiler | None = None,
    ) -> None:
        self.context_window = max(0, context_window)
        self.max_context_tokens = max(12, max_context_tokens)
        self.profiler = profiler or GraphBuildProfiler.disabled()

    def set_profiler(self, profiler: GraphBuildProfiler | None) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()

    def enrich(self, graph: DocumentGraph) -> None:
        if self.context_window <= 0:
            return

        with self.profiler.measure(
            name="document_graph_builder.asset_nearby_text_enrichment",
            input_counts={
                "tables": len(graph.tables),
                "pictures": len(graph.pictures),
            },
        ) as stage:
            elements_by_table_id, elements_by_picture_id = self._index_asset_elements(
                graph
            )
            enriched_assets = 0
            for asset_collection, elements_by_asset_id in (
                (graph.tables, elements_by_table_id),
                (graph.pictures, elements_by_picture_id),
            ):
                for asset_id, asset in asset_collection.items():
                    asset_element = elements_by_asset_id.get(asset_id)
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
                    enriched_assets += int(bool(asset.metadata.nearby_text))
            stage.output_counts["enriched_assets"] = enriched_assets

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
    def _index_asset_elements(
        graph: DocumentGraph,
    ) -> tuple[dict[str, CanonicalElement], dict[str, CanonicalElement]]:
        """Builds table_id/picture_id -> owning element lookups in one pass
        over the document's elements, instead of scanning every element
        again for every table/picture asset."""
        elements_by_table_id: dict[str, CanonicalElement] = {}
        elements_by_picture_id: dict[str, CanonicalElement] = {}
        for element in graph.elements.values():
            if element.table_id is not None:
                elements_by_table_id.setdefault(element.table_id, element)
            if element.picture_id is not None:
                elements_by_picture_id.setdefault(element.picture_id, element)
        return elements_by_table_id, elements_by_picture_id

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
