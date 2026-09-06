from src.application.workflows.parsing.builders.chunking.builders.section_chunk.section_chunk_builder import (
    SectionChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.structured_marker_matcher import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_document_evidence_context import (
    StructuredDocumentEvidenceContext,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_spec_factory import (
    StructuredFamilySpecFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_spec_selection import (
    StructuredFamilySpecSelection,
)
from src.application.workflows.parsing.builders.chunking.builders.structured_section_fragment_builder import (
    StructuredSectionFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.runtime.chunking_runtime_factory import (
    ChunkingRuntimeFactory,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.profiling import GraphBuildProfiler
from src.domain.common import DocumentType, ElementType, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class _CountingMatcher(StructuredMarkerMatcher):
    def __init__(self) -> None:
        self.normalized_values: list[str] = []
        self.document_scan_count = 0
        self.tracked_document_text = ""

    def normalize(self, value: str | None) -> str:
        self.normalized_values.append(str(value or ""))
        return super().normalize(value)

    def contains_any_normalized(self, normalized_text, markers):
        if normalized_text == self.tracked_document_text:
            self.document_scan_count += 1
        return super().contains_any_normalized(normalized_text, markers)


class _RecordingFamilyBuilder:
    def __init__(self) -> None:
        self.document_context_ids: list[int] = []

    def build(self, *, context, marker_tuning) -> StructuredFamilySpecSelection:
        self.document_context_ids.append(id(context.document_context))
        return StructuredFamilySpecSelection()


def _section(section_id: str, title: str, order: int) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
        level=1,
        section_path=[title],
        source=SourceLocation(page_start=order, page_end=order),
        sequence_number=order,
    )


def _element(element_id: str, text: str, order: int) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        reading_order=order,
        source=SourceLocation(page_start=order, page_end=order),
    )


def test_document_marker_group_is_scanned_once() -> None:
    matcher = _CountingMatcher()
    context = StructuredDocumentEvidenceContext.build(
        document_title="Engine documentation",
        document_sections_combined_text="Technical data > Inspection report",
        matcher=matcher,
    )
    matcher.tracked_document_text = context.normalized_section_text
    markers = (EvidenceMarker("inspection report", MarkerStrength.STRONG),)

    assert context.contains_any(markers)
    assert context.contains_any(markers)
    assert matcher.document_scan_count == 1


def test_document_chunking_reuses_context_and_profiles_each_family() -> None:
    matcher = _CountingMatcher()
    family_builder = _RecordingFamilyBuilder()
    profiler = GraphBuildProfiler(document_id="doc_001")
    structured_builder = StructuredSectionFragmentBuilder(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=100, chunk_overlap=10),
        marker_matcher=matcher,
        spec_factory=StructuredFamilySpecFactory(
            family_builders=[family_builder],
            enable_benchmark_tuning=False,
        ),
    )
    builder = SectionChunkBuilder(
        runtime_factory=ChunkingRuntimeFactory(
            structured_fragment_builder=structured_builder,
        ),
        profiler=profiler,
    )
    sections = [
        _section("sec_1", "Section One", 1),
        _section("sec_2", "Section Two", 2),
    ]

    builder.build_document_chunk_payloads(
        document_title="Engine manual",
        document_type=DocumentType.MANUAL,
        sections=sections,
        section_elements_by_id={
            "sec_1": [_element("el_1", "First section evidence.", 1)],
            "sec_2": [_element("el_2", "Second section evidence.", 2)],
        },
    )

    assert len(set(family_builder.document_context_ids)) == 1
    assert matcher.normalized_values.count("Section One Section Two") == 1
    family_metric = next(
        metric
        for metric in profiler.stage_metrics
        if metric.name.endswith("._RecordingFamilyBuilder")
    )
    assert family_metric.operations["invocations"] == 2
