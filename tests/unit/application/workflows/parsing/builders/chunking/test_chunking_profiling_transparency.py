from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.application.workflows.parsing.profiling import GraphBuildProfiler
from src.domain.common import DocumentType, ElementType, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def test_fragment_profiling_does_not_change_chunk_payloads() -> None:
    section = DocumentSection(
        section_id="sec_001",
        document_id="doc_001",
        title="5.2 Operating procedure",
        level=2,
        parent_section_id="sec_parent",
        section_path=["5 Operation", "5.2 Operating procedure"],
        source=SourceLocation(page_start=12, page_end=12),
        sequence_number=1,
    )
    elements = [
        CanonicalElement(
            element_id="el_001",
            document_id="doc_001",
            element_type=ElementType.TEXT,
            text="Open the supply valve, verify pressure, and start the pump.",
            reading_order=1,
            source=SourceLocation(page_start=12, page_end=12),
        )
    ]
    baseline = SectionChunkBuilder(
        profiler=GraphBuildProfiler.disabled(),
    ).build_chunk_payloads(
        document_title="Equipment manual",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
    )
    profiled = SectionChunkBuilder(
        profiler=GraphBuildProfiler(),
    ).build_chunk_payloads(
        document_title="Equipment manual",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
    )

    assert profiled == baseline
