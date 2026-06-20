from pathlib import Path

from scripts.debug_parse_document import build_report
from src.application.workflows.parsing import (
    CanonicalElement as ParsedCanonicalElement,
    RawParsedDocument,
)
from src.application.workflows.parsing.builders import (
    DocumentGraphBuilder,
    SectionBuilder,
)
from src.domain.common import BoundingBox, ElementType
from src.domain.document import DocumentHashes
from src.shared.ids import IdGenerator


def make_parsed_element(
    *,
    element_id: str,
    element_type: ElementType,
    order_index: int,
    text: str | None,
    page_start: int,
    metadata: dict | None = None,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page_start,
        page_end=page_start,
        bbox=BoundingBox(x1=1, y1=2, x2=3, y2=4),
        order_index=order_index,
        section_title=text if element_type == ElementType.SECTION_HEADER else None,
        raw_ref=element_id,
        metadata=metadata or {},
    )


def make_builder() -> DocumentGraphBuilder:
    id_generator = IdGenerator()
    return DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=SectionBuilder(id_generator),
    )


def make_raw_parsed_document() -> RawParsedDocument:
    return RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=2,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )


def test_build_report_includes_structural_profile_inference_section() -> None:
    builder = make_builder()
    raw_parsed_document = make_raw_parsed_document()
    canonical_elements = [
        make_parsed_element(
            element_id="hdr_1",
            element_type=ElementType.SECTION_HEADER,
            order_index=1,
            text="Maintenance Procedure",
            page_start=1,
            metadata={"heading_level": 1},
        ),
        make_parsed_element(
            element_id="txt_1",
            element_type=ElementType.TEXT,
            order_index=2,
            text="Follow the maintenance procedure before servicing the pump system.",
            page_start=1,
        ),
        make_parsed_element(
            element_id="txt_2",
            element_type=ElementType.LIST_ITEM,
            order_index=3,
            text="Disconnect power and inspect the filter assembly.",
            page_start=1,
        ),
    ]
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=canonical_elements,
        raw_parsed_document=raw_parsed_document,
    )

    report = build_report(
        input_path=Path("data/input/pump_manual.pdf"),
        output_path=Path("outputs/debug_parsing/pump_manual_parsing_report.md"),
        file_hash="file_hash_001",
        content_hash="content_hash_001",
        raw_parsed_document=raw_parsed_document,
        canonical_elements=canonical_elements,
        document_graph=graph,
        section_build_result=builder.last_section_build_result,
    )

    assert "## Structural Profile Inference" in report
    assert "selected profile" in report
    assert "model classification: `not run in parsing debug script`" in report
