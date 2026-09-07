from src.application.workflows.parsing.builders import SectionBuilder
from src.application.workflows.parsing.builders.chunking.builders.section_chunk.section_chunk_builder import (
    SectionChunkBuilder,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import ElementType, ParserMetadata, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement
from src.shared.ids import IdGenerator


def _parsed_header(
    element_id: str,
    text: str,
    order: int,
    *,
    level: int,
    furniture: bool = False,
) -> ParsedCanonicalElement:
    metadata = {"heading_level": level}
    if furniture:
        metadata["layout_is_page_furniture"] = True
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.SECTION_HEADER,
        text=text,
        page_start=order,
        page_end=order,
        order_index=order,
        metadata=metadata,
    )


def test_recurring_header_does_not_break_numbered_section_hierarchy() -> None:
    elements = [
        _parsed_header("chapter", "2 Safety", 1, level=1),
        _parsed_header(
            "running_header",
            "Technical Operating Manual",
            2,
            level=1,
            furniture=True,
        ),
        _parsed_header("section", "2.1 Intended use", 3, level=1),
        ParsedCanonicalElement(
            element_id="body",
            document_id="doc_001",
            element_type=ElementType.TEXT,
            text="Use the equipment only for its intended application.",
            page_start=3,
            page_end=3,
            order_index=4,
        ),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert "running_header" not in result.header_section_ids
    assert result.element_section_paths["body"] == [
        "2 Safety",
        "2.1 Intended use",
    ]


def test_recurring_footer_is_not_emitted_into_final_chunk_content() -> None:
    section = DocumentSection(
        section_id="sec_maintenance",
        document_id="doc_001",
        title="9 Maintenance",
        section_path=["9 Maintenance"],
        source=SourceLocation(page_start=20, page_end=20),
    )
    elements = [
        CanonicalElement(
            element_id="body",
            document_id="doc_001",
            element_type=ElementType.TEXT,
            text="Inspect the compressor and replace worn components.",
            source=SourceLocation(page_start=20, page_end=20),
            parser_metadata=ParserMetadata(parser_name="docling"),
        ),
        CanonicalElement(
            element_id="footer",
            document_id="doc_001",
            element_type=ElementType.TEXT,
            text="Document A-104 | 20/206 | 2026-09-07",
            source=SourceLocation(page_start=20, page_end=20),
            parser_metadata=ParserMetadata(
                parser_name="docling",
                extra={"layout_is_page_furniture": True},
            ),
        ),
    ]

    payloads = SectionChunkBuilder().build_chunk_payloads(
        document_title="Compressor Manual",
        section=section,
        elements=elements,
    )

    content = "\n".join(payload.content for payload in payloads)
    assert "Inspect the compressor" in content
    assert "A-104" not in content
    assert "20/206" not in content
