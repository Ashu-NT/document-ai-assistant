import copy

import pytest

from src.application.validation.common import ValidationResult

from src.application.validation.document import DocumentGraphValidator

from src.application.workflows.parsing import (
    ParsedCanonicalElement,
    ParsingWorkflow,
    RawParsedDocument,
)

from src.domain.common import ElementType

from src.shared.exceptions import SchemaValidationError

from src.shared.ids import IdGenerator

class FakeParser:
    def __init__(self, raw_parsed_document: RawParsedDocument) -> None:
        self.raw_parsed_document = raw_parsed_document
        self.calls: list[str] = []
        self.enable_ocr_overrides: list[bool | None] = []

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
        self.calls.append(file_path)
        self.enable_ocr_overrides.append(enable_ocr_override)
        return self.raw_parsed_document

class FakeNormalizer:
    def __init__(self, canonical_elements: list[ParsedCanonicalElement]) -> None:
        self.canonical_elements = canonical_elements
        self.calls: list[tuple[RawParsedDocument, str]] = []

    def normalize(
        self,
        raw_parsed_document: RawParsedDocument,
        document_id: str,
    ) -> list[ParsedCanonicalElement]:
        self.calls.append((raw_parsed_document, document_id))
        return self.canonical_elements

class FakeDocumentGraphBuilder:
    def __init__(self, document_graph) -> None:
        self.document_graph = document_graph
        self.calls: list[dict] = []

    def build(self, **kwargs):
        self.calls.append(kwargs)
        return self.document_graph

class FakeCanonicalElementOCREnricher:
    def __init__(self, enriched_elements: list[ParsedCanonicalElement]) -> None:
        self.enriched_elements = enriched_elements
        self.calls: list[tuple[list[ParsedCanonicalElement], object]] = []

    def enrich(self, canonical_elements, *, activity_context=None):
        self.calls.append((canonical_elements, activity_context))
        return self.enriched_elements

class SpyDocumentGraphValidator:
    def __init__(self, validation_result: ValidationResult | None = None) -> None:
        self.validation_result = validation_result or ValidationResult()
        self.calls = []

    def validate(self, value):
        self.calls.append(value)
        return self.validation_result

def test_parse_runs_optional_ocr_enricher_before_graph_build(
    sample_document_graph,
) -> None:
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=3,
        raw_document=object(),
        parser_name="docling",
    )
    canonical_elements = [
        ParsedCanonicalElement(
            element_id="pic_001",
            document_id="doc_placeholder",
            element_type=ElementType.PICTURE,
            order_index=1,
            metadata={"image_path": "outputs/images/pic_001.png"},
        )
    ]
    enriched_elements = [
        ParsedCanonicalElement(
            element_id="pic_001",
            document_id="doc_placeholder",
            element_type=ElementType.PICTURE,
            order_index=1,
            metadata={
                "image_path": "outputs/images/pic_001.png",
                "ocr_text": "FILTER HOUSING HP-001",
            },
        )
    ]
    parser = FakeParser(raw_parsed_document)
    normalizer = FakeNormalizer(canonical_elements)
    builder = FakeDocumentGraphBuilder(sample_document_graph)
    enricher = FakeCanonicalElementOCREnricher(enriched_elements)
    workflow = ParsingWorkflow(
        parser=parser,
        normalizer=normalizer,
        document_graph_builder=builder,
        id_generator=IdGenerator(),
        canonical_element_ocr_enricher=enricher,
    )

    workflow.parse(
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
        content_hash="content_hash_001",
    )

    assert len(enricher.calls) == 1
    assert enricher.calls[0][0] == canonical_elements
    assert builder.calls[0]["canonical_elements"] == enriched_elements

def test_parse_forwards_enable_ocr_override_to_parser(sample_document_graph) -> None:
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=3,
        raw_document=object(),
        parser_name="docling",
    )
    parser = FakeParser(raw_parsed_document)
    normalizer = FakeNormalizer([])
    builder = FakeDocumentGraphBuilder(copy.deepcopy(sample_document_graph))
    workflow = ParsingWorkflow(
        parser=parser,
        normalizer=normalizer,
        document_graph_builder=builder,
        id_generator=IdGenerator(),
    )

    workflow.parse(
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
        content_hash="content_hash_001",
        enable_ocr_override=True,
    )

    assert parser.enable_ocr_overrides == [True]

def test_parse_defaults_enable_ocr_override_to_none(sample_document_graph) -> None:
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=3,
        raw_document=object(),
        parser_name="docling",
    )
    parser = FakeParser(raw_parsed_document)
    normalizer = FakeNormalizer([])
    builder = FakeDocumentGraphBuilder(copy.deepcopy(sample_document_graph))
    workflow = ParsingWorkflow(
        parser=parser,
        normalizer=normalizer,
        document_graph_builder=builder,
        id_generator=IdGenerator(),
    )

    workflow.parse(
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
        content_hash="content_hash_001",
    )

    assert parser.enable_ocr_overrides == [None]
