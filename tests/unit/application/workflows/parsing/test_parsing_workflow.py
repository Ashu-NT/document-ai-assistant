import copy

import pytest

from src.application.validation.common import ValidationResult
from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing import (
    CanonicalElement as ParsedCanonicalElement,
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

    def parse(self, file_path: str) -> RawParsedDocument:
        self.calls.append(file_path)
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


def test_parse_orchestrates_parsing_normalization_build_and_validation(
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
            element_id="canon_001",
            document_id="doc_placeholder",
            element_type=ElementType.TEXT,
            text="Replacement instructions.",
            order_index=1,
        )
    ]
    parser = FakeParser(raw_parsed_document)
    normalizer = FakeNormalizer(canonical_elements)
    graph = copy.deepcopy(sample_document_graph)
    builder = FakeDocumentGraphBuilder(graph)
    validator = SpyDocumentGraphValidator()
    workflow = ParsingWorkflow(
        parser=parser,
        normalizer=normalizer,
        document_graph_builder=builder,
        id_generator=IdGenerator(),
        document_graph_validator=validator,
    )

    result = workflow.parse(
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
        content_hash="content_hash_001",
    )

    assert parser.calls == ["data/input/pump_manual.pdf"]
    assert len(normalizer.calls) == 1
    assert normalizer.calls[0][0] == raw_parsed_document
    assert normalizer.calls[0][1].startswith("doc_")
    assert len(builder.calls) == 1
    assert builder.calls[0]["document_id"] == normalizer.calls[0][1]
    assert builder.calls[0]["file_path"] == "data/input/pump_manual.pdf"
    assert builder.calls[0]["hashes"].file_hash == "file_hash_001"
    assert builder.calls[0]["hashes"].content_hash == "content_hash_001"
    assert builder.calls[0]["canonical_elements"] == canonical_elements
    assert builder.calls[0]["raw_parsed_document"] == raw_parsed_document
    assert validator.calls == [graph]
    assert result.document_id == graph.document.document_id
    assert result.page_count == 3
    assert result.element_count == len(graph.elements)
    assert result.section_count == len(graph.sections)
    assert result.chunk_count == len(graph.chunks)


def test_parse_emits_progress_messages_for_major_substages(
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
            element_id="canon_001",
            document_id="doc_placeholder",
            element_type=ElementType.TEXT,
            text="Replacement instructions.",
            order_index=1,
        )
    ]
    parser = FakeParser(raw_parsed_document)
    normalizer = FakeNormalizer(canonical_elements)
    builder = FakeDocumentGraphBuilder(copy.deepcopy(sample_document_graph))
    validator = SpyDocumentGraphValidator()
    workflow = ParsingWorkflow(
        parser=parser,
        normalizer=normalizer,
        document_graph_builder=builder,
        id_generator=IdGenerator(),
        document_graph_validator=validator,
    )
    messages: list[str] = []

    workflow.parse(
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
        content_hash="content_hash_001",
        progress_callback=messages.append,
    )

    assert any("Parsing workflow started for pump_manual.pdf." in message for message in messages)
    assert any("Docling conversion started for pump_manual.pdf." in message for message in messages)
    assert any("Docling conversion completed in" in message for message in messages)
    assert any("Normalizing Docling output into canonical elements" in message for message in messages)
    assert any("Canonical normalization completed in" in message for message in messages)
    assert any("Building document graph from 1 canonical element(s)" in message for message in messages)
    assert any("Document graph build completed in" in message for message in messages)
    assert any("Validating document graph" in message for message in messages)
    assert any("Document graph validation completed in" in message for message in messages)
    assert any("Parsing workflow completed in" in message for message in messages)


def test_parse_raises_schema_validation_error_when_graph_validation_fails(
    sample_document_graph,
) -> None:
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=1,
        raw_document=object(),
        parser_name="docling",
    )
    parser = FakeParser(raw_parsed_document)
    normalizer = FakeNormalizer([])
    builder = FakeDocumentGraphBuilder(sample_document_graph)
    validation_result = ValidationResult()
    validation_result.add_issue(
        field="chunks",
        message="Chunk document_id does not match graph document_id.",
        code="document_graph.chunk.document_mismatch",
    )
    validator = SpyDocumentGraphValidator(validation_result)
    workflow = ParsingWorkflow(
        parser=parser,
        normalizer=normalizer,
        document_graph_builder=builder,
        id_generator=IdGenerator(),
        document_graph_validator=validator,
    )

    with pytest.raises(SchemaValidationError):
        workflow.parse(
            file_path="data/input/pump_manual.pdf",
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        )

    assert parser.calls == ["data/input/pump_manual.pdf"]
    assert validator.calls == [sample_document_graph]


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
