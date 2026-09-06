from src.application.workflows.parsing.builders.chunking.builders.structured import (
    StructuredFamilySpecFactory,
    StructuredSectionWindowSpec,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_element_text_resolver import (
    StructuredElementTextResolver,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    is_furniture_or_embedded_picture,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.structured_marker_match_policy import (
    StructuredMarkerMatchPolicy,
)
from src.domain.common import ChunkType, DocumentType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement
from src.application.workflows.parsing.builders.chunking.builders.fragment.table_chunk_eligibility_policy import (
    TableChunkEligibilityPolicy,
)
from src.application.workflows.parsing.profiling import GraphBuildProfiler

class StructuredSectionFragmentBuilder:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        spec_factory: StructuredFamilySpecFactory | None = None,
        marker_matcher: StructuredMarkerMatcher | None = None,
        marker_match_policy: StructuredMarkerMatchPolicy | None = None,
        table_chunk_eligibility_policy: TableChunkEligibilityPolicy | None = None,
        profiler: GraphBuildProfiler | None = None,
    ) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()
        self.text_splitter = text_splitter
        self.spec_factory = spec_factory or StructuredFamilySpecFactory()
        self.marker_matcher = marker_matcher or StructuredMarkerMatcher()
        self.marker_match_policy = (
            marker_match_policy
            or StructuredMarkerMatchPolicy(matcher=self.marker_matcher)
        )
        self.table_chunk_eligibility_policy = (
            table_chunk_eligibility_policy
            or TableChunkEligibilityPolicy(
                text_splitter=text_splitter,
            )
        )
        self.spec_factory.set_profiler(self.profiler)

    def set_profiler(self, profiler: GraphBuildProfiler | None) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()
        self.spec_factory.set_profiler(self.profiler)

    def build(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        document_sections_combined_text: str = "",
    ) -> tuple[list[ChunkFragment], set[str]]:
        ordered_elements = [
            element
            for element in elements
            if self._is_structurable_element(element)
        ]
        if not ordered_elements:
            return [], set()

        selection = self.spec_factory.build(
            document_title=document_title,
            document_type=document_type,
            section=section,
            elements=ordered_elements,
            normalizer=self.marker_matcher.normalize,
            document_sections_combined_text=document_sections_combined_text,
        )
        if not selection.specs:
            return [], set()

        windows_by_spec: list[
            tuple[StructuredSectionWindowSpec, list[list[CanonicalElement]]]
        ] = []
        with self.profiler.aggregate(
            name="structured_section_fragment_builder.collect_windows",
            input_counts={"sections": 1, "specs": len(selection.specs)},
        ) as stage:
            for spec in selection.specs:
                windows_by_spec.append(
                    (spec, self._collect_windows(ordered_elements, spec))
                )
            stage.output_counts["windows"] = sum(
                len(windows) for _, windows in windows_by_spec
            )

        fragments: list[ChunkFragment] = []
        consumed_element_ids: set[str] = set()
        with self.profiler.aggregate(
            name="structured_section_fragment_builder.materialize_fragments",
            input_counts={
                "sections": 1,
                "windows": sum(len(windows) for _, windows in windows_by_spec),
            },
        ) as stage:
            for spec, windows in windows_by_spec:
                for window in windows:
                    fragment = self._build_fragment(
                        section=section,
                        elements=window,
                        spec=spec,
                    )
                    if fragment is None:
                        continue
                    fragments.append(fragment)
                    consumed_element_ids.update(fragment.element_ids)
            stage.output_counts["fragments"] = len(fragments)

        if selection.consume_all_elements and fragments:
            consumed_element_ids.update(
                element.element_id
                for element in ordered_elements
            )

        return (
            sorted(fragments, key=lambda fragment: fragment.order_index),
            consumed_element_ids,
        )

    def _collect_windows(
        self,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
    ) -> list[list[CanonicalElement]]:
        anchor_indexes = [
            index
            for index, element in enumerate(elements)
            if self.marker_match_policy.matches(
                StructuredElementTextResolver.resolve(element) or "",
                spec.anchor_markers,
            )
        ]
        if not anchor_indexes:
            if spec.include_full_section_if_no_anchor and elements:
                return [list(elements)]
            else:
                return []

        windows: list[tuple[int, int]] = []
        for anchor_index in anchor_indexes:
            start_index = max(0, anchor_index - spec.radius_before)
            end_index = min(len(elements) - 1, anchor_index + spec.radius_after)
            windows.append((start_index, end_index))

        merged_windows = self._merge_windows(windows)
        window_elements = [
            elements[start_index : end_index + 1]
            for start_index, end_index in merged_windows
        ]
        if spec.combine_all_windows and window_elements:
            combined_elements: list[CanonicalElement] = []
            seen_element_ids: set[str] = set()
            for window in window_elements:
                for element in window:
                    if element.element_id in seen_element_ids:
                        continue
                    seen_element_ids.add(element.element_id)
                    combined_elements.append(element)
            return [combined_elements]
        return window_elements

    def _build_fragment(
        self,
        *,
        section: DocumentSection,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
    ) -> ChunkFragment | None:
        texts: list[str] = []
        for element in elements:
            text = StructuredElementTextResolver.resolve(element)
            if text:
                texts.append(text)
        if not texts:
            return None

        content = "\n".join(texts).strip()
        # Word count, not self.text_splitter.count_tokens(): min_tokens is a
        # "is there enough substance here" gate, not an embedding-budget
        # check, so it must stay stable regardless of which ChunkTokenCounter
        # is configured -- riding on the pluggable counter let a structured
        # family claim (and permanently chunk-type-lock) short elements more
        # aggressively whenever a real-subword-token counter was active.
        if len(content.split()) < spec.min_tokens:
            return None

        token_count = self.text_splitter.count_tokens(content)

        first_element = elements[0]
        return ChunkFragment(
            text=content,
            chunk_type=spec.chunk_type,
            standalone=True,
            section_id=section.section_id,
            section_title=section.title,
            section_path=list(section.section_path),
            section_level=section.level,
            parent_section_id=section.parent_section_id,
            element_ids=[element.element_id for element in elements],
            table_ids=[
                element.table_id
                for element in elements
                if element.table_id is not None
            ],
            picture_ids=[
                element.picture_id
                for element in elements
                if element.picture_id is not None
            ],
            page_start=min(
                (
                    element.source.page_start
                    for element in elements
                    if element.source.page_start is not None
                ),
                default=first_element.source.page_start,
            ),
            page_end=max(
                (
                    element.source.page_end
                    for element in elements
                    if element.source.page_end is not None
                ),
                default=first_element.source.page_end,
            ),
            token_count=token_count,
            order_index=first_element.reading_order or 0,
        )

    @staticmethod
    def _merge_windows(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not windows:
            return []

        ordered_windows = sorted(windows)
        merged_windows = [ordered_windows[0]]
        for start_index, end_index in ordered_windows[1:]:
            previous_start, previous_end = merged_windows[-1]
            if start_index <= previous_end + 1:
                merged_windows[-1] = (
                    previous_start,
                    max(previous_end, end_index),
                )
                continue
            merged_windows.append((start_index, end_index))
        return merged_windows

    def _is_structurable_element(
        self,
        element: CanonicalElement,
    ) -> bool:
        if element.element_type not in {
            ElementType.TEXT,
            ElementType.LIST_ITEM,
            ElementType.KEY_VALUE,
            ElementType.CODE,
            ElementType.TABLE,
            ElementType.PICTURE,
        }:
            return False
        if is_furniture_or_embedded_picture(element):
            return False

        if (
            element.table_id is not None
            or element.element_type == ElementType.TABLE
        ):
            if not self.table_chunk_eligibility_policy.should_chunk(
                element
            ):
                return False

        return bool(
            StructuredElementTextResolver.resolve(element)
        )

