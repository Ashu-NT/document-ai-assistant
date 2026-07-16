from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.application.workflows.parsing.builders.chunking.builders.section_chunk_skipper import (
    SectionChunkSkipper,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.config.settings import chunking_settings
from src.domain.common import DocumentType, ElementType, ParserMetadata, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def make_section(
    *,
    title: str,
    section_path: list[str],
    page: int,
    parent_section_id: str | None,
) -> DocumentSection:
    return DocumentSection(
        section_id="sec_001",
        document_id="doc_001",
        title=title,
        level=2 if parent_section_id is not None else 1,
        parent_section_id=parent_section_id,
        section_path=section_path,
        source=SourceLocation(page_start=page, page_end=page),
        sequence_number=1,
    )


def make_element(
    *,
    element_id: str,
    element_type: ElementType,
    text: str,
    page: int,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        reading_order=1,
        source=SourceLocation(page_start=page, page_end=page),
    )


def test_section_chunk_skipper_recovers_late_contents_polluted_section() -> None:
    skipper = SectionChunkSkipper(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
    )
    section = make_section(
        title="Extended order code: Cerabar M",
        section_path=[
            "8 Commissioning",
            "Safety Instructions",
            "Cerabar M PMC51, PMP51, PMP55",
            "Table of contents",
            "Extended order code",
            "Basic specifications",
            "Extended order code: Cerabar M",
        ],
        page=36,
        parent_section_id="sec_parent",
    )
    elements = [
        make_element(
            element_id="tbl_1",
            element_type=ElementType.TABLE,
            text=(
                "| Position 1, 2 (Approval) | Description |\n"
                "|---|---|\n"
                "| PMC51 PMP5x BG | ATEX II 3 G Ex ic IIC T6...T4 Gc |\n"
                "| IE | IECEx Ex ic IIC T6...T4 Gc |"
            ),
            page=36,
        )
    ]

    should_skip = skipper.should_skip_section(
        document_title="Pressure transmitter report",
        section=section,
        elements=elements,
    )

    assert should_skip is False


def test_section_chunk_skipper_still_skips_early_contents_child_section() -> None:
    skipper = SectionChunkSkipper(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
    )
    section = make_section(
        title="Introduction",
        section_path=["Contents", "Introduction"],
        page=2,
        parent_section_id="sec_contents",
    )
    elements = [
        make_element(
            element_id="txt_1",
            element_type=ElementType.TEXT,
            text="Introduction 5",
            page=2,
        )
    ]

    should_skip = skipper.should_skip_section(
        document_title="Hydraulic Pump Manual",
        section=section,
        elements=elements,
    )

    assert should_skip is True


def _make_ambiguous_front_matter_section_and_elements(
    *, layout_is_front_matter: bool
) -> tuple[DocumentSection, list[CanonicalElement]]:
    """A section whose token-heuristic path alone returns False (a single
    long, punctuated sentence trips the "not front matter" early-return at
    line ~154), used to prove the layout signal is what changes the
    outcome, not the existing heuristics."""
    section = make_section(
        title="Overview",
        section_path=["Overview"],
        page=1,
        parent_section_id=None,
    )
    element = make_element(
        element_id="txt_1",
        element_type=ElementType.TEXT,
        text="This device measures pressure using a robust ceramic sensor cell.",
        page=1,
    )
    if layout_is_front_matter:
        element.parser_metadata = ParserMetadata(
            parser_name="docling",
            extra={"layout_is_front_matter": True},
        )
    return section, [element]


def test_layout_front_matter_signal_is_ignored_when_flag_is_off(monkeypatch) -> None:
    monkeypatch.setattr(chunking_settings, "use_layout_front_matter_signal", False)
    skipper = SectionChunkSkipper(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
    )
    section, elements = _make_ambiguous_front_matter_section_and_elements(
        layout_is_front_matter=True
    )

    should_skip = skipper.should_skip_section(
        document_title="Pressure transmitter report",
        section=section,
        elements=elements,
    )

    assert should_skip is False


def test_layout_front_matter_signal_skips_section_when_flag_is_on(monkeypatch) -> None:
    monkeypatch.setattr(chunking_settings, "use_layout_front_matter_signal", True)
    skipper = SectionChunkSkipper(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
    )
    section, elements = _make_ambiguous_front_matter_section_and_elements(
        layout_is_front_matter=True
    )

    should_skip = skipper.should_skip_section(
        document_title="Pressure transmitter report",
        section=section,
        elements=elements,
    )

    assert should_skip is True


def test_layout_front_matter_signal_on_but_absent_falls_back_to_existing_heuristics(
    monkeypatch,
) -> None:
    monkeypatch.setattr(chunking_settings, "use_layout_front_matter_signal", True)
    skipper = SectionChunkSkipper(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
    )
    section, elements = _make_ambiguous_front_matter_section_and_elements(
        layout_is_front_matter=False
    )

    should_skip = skipper.should_skip_section(
        document_title="Pressure transmitter report",
        section=section,
        elements=elements,
    )

    assert should_skip is False


def test_section_chunk_builder_emits_structured_chunk_for_contents_polluted_section() -> None:
    builder = SectionChunkBuilder()
    section = make_section(
        title="Extended order code: Cerabar M",
        section_path=[
            "8 Commissioning",
            "Safety Instructions",
            "Cerabar M PMC51, PMP51, PMP55",
            "Table of contents",
            "Extended order code",
            "Basic specifications",
            "Extended order code: Cerabar M",
        ],
        page=36,
        parent_section_id="sec_parent",
    )
    elements = [
        make_element(
            element_id="txt_1",
            element_type=ElementType.TEXT,
            text="The following specifications reproduce an extract from the product structure.",
            page=36,
        ),
        make_element(
            element_id="tbl_1",
            element_type=ElementType.TABLE,
            text=(
                "| Position 1, 2 (Approval) | Description |\n"
                "|---|---|\n"
                "| PMC51 PMP5x BG | ATEX II 3 G Ex ic IIC T6...T4 Gc |\n"
                "| IE | IECEx Ex ic IIC T6...T4 Gc |"
            ),
            page=36,
        ),
    ]

    payloads = builder.build_chunk_payloads(
        document_title="Pressure transmitter report",
        section=section,
        elements=elements,
        document_type=DocumentType.REPORT,
    )

    approval_payload = next(
        payload
        for payload in payloads
        if payload.section_path
        == [
            "Safety Instructions",
            "Extended order code: Cerabar M",
            "Basic specifications",
        ]
    )

    assert "PMC51 PMP5x BG" in approval_payload.content
    assert "IECEx Ex ic IIC T6...T4 Gc" in approval_payload.content
