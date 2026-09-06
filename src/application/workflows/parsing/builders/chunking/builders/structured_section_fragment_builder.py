from src.application.workflows.parsing.builders.chunking.builders.structured import (
    StructuredFamilySpecFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration import (
    StructuredReferenceEvidencePolicy,
    StructuredWindowArbitrator,
    StructuredWindowCandidateBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
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
        candidate_builder: StructuredWindowCandidateBuilder | None = None,
        window_arbitrator: StructuredWindowArbitrator | None = None,
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
        self.candidate_builder = candidate_builder or StructuredWindowCandidateBuilder(
            marker_match_policy=self.marker_match_policy,
            reference_policy=StructuredReferenceEvidencePolicy(
                matcher=self.marker_matcher,
            ),
        )
        self.window_arbitrator = window_arbitrator or StructuredWindowArbitrator()
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

        with self.profiler.aggregate(
            name="structured_section_fragment_builder.collect_windows",
            input_counts={"sections": 1, "specs": len(selection.specs)},
        ) as stage:
            candidates = self.candidate_builder.build(
                section=section,
                elements=ordered_elements,
                specs=selection.specs,
            )
            selected_candidates = self.window_arbitrator.select(candidates)
            stage.output_counts["candidate_windows"] = len(candidates)
            stage.output_counts["selected_windows"] = len(selected_candidates)

        fragments: list[ChunkFragment] = []
        consumed_element_ids: set[str] = set()
        with self.profiler.aggregate(
            name="structured_section_fragment_builder.materialize_fragments",
            input_counts={
                "sections": 1,
                "windows": len(selected_candidates),
            },
        ) as stage:
            for candidate in selected_candidates:
                fragment = self._build_fragment(
                    section=section,
                    elements=list(candidate.elements),
                    spec=candidate.spec,
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

