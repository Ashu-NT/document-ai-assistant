from src.application.workflows.parsing.builders.chunking.builders.fragment.chunk_fragment_builder import (
    ChunkFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ElementType, ParserMetadata, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def test_filtered_local_header_text_remains_available_to_chunking() -> None:
    section = DocumentSection(
        section_id="sec_001",
        document_id="doc_001",
        title="Maintenance",
        section_path=["3 Maintenance"],
    )
    elements = [
        CanonicalElement(
            element_id="hdr_warning",
            document_id="doc_001",
            element_type=ElementType.SECTION_HEADER,
            text="WARNING",
            reading_order=1,
            source=SourceLocation(page_start=7, page_end=7),
            parser_metadata=ParserMetadata(
                parser_name="docling",
                extra={"structural_heading": False},
            ),
        ),
        CanonicalElement(
            element_id="txt_warning",
            document_id="doc_001",
            element_type=ElementType.TEXT,
            text="Disconnect power before opening the enclosure.",
            reading_order=2,
            source=SourceLocation(page_start=7, page_end=7),
        ),
    ]
    builder = ChunkFragmentBuilder(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=200, chunk_overlap=20),
    )

    fragments = builder.build_section_fragments(
        document_title="Service manual",
        document_type=None,
        section=section,
        elements=elements,
    )

    assert any("WARNING" in fragment.text for fragment in fragments)
    assert all(fragment.section_path == section.section_path for fragment in fragments)
