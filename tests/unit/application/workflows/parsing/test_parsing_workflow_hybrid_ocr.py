from src.application.workflows.parsing import CanonicalElement, ParsingWorkflow, RawParsedDocument
from src.domain.common import ElementType
from src.shared.ids import IdGenerator


class FakeParser:
    def __init__(self, raw_parsed_document: RawParsedDocument) -> None:
        self.raw_parsed_document = raw_parsed_document

    def parse(self, file_path: str) -> RawParsedDocument:
        return self.raw_parsed_document


class FakeNormalizer:
    def __init__(self, canonical_elements: list[CanonicalElement]) -> None:
        self.canonical_elements = canonical_elements

    def normalize(self, raw_parsed_document: RawParsedDocument, document_id: str):
        return self.canonical_elements


class FakeGraphBuilder:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.calls: list[dict] = []

    def build(self, **kwargs):
        self.calls.append(kwargs)
        return self.graph


class FakePageOCRFallbackWorkflow:
    def __init__(self, enriched_elements: list[CanonicalElement]) -> None:
        self.enriched_elements = enriched_elements
        self.calls: list[tuple[str, int | None]] = []

    def run(self, *, file_path: str, canonical_elements, page_count: int | None, activity_context=None):
        self.calls.append((file_path, page_count))
        return type(
            "MergeResult",
            (),
            {
                "canonical_elements": self.enriched_elements,
                "ocr_trace": None,
            },
        )()


def test_parse_runs_optional_page_ocr_fallback_before_graph_build(sample_document_graph) -> None:
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=2,
        raw_document=object(),
        parser_name="docling",
    )
    canonical_elements = [
        CanonicalElement(
            element_id="canon_001",
            document_id="doc_placeholder",
            element_type=ElementType.TEXT,
            text="Original text",
            order_index=1,
            page_start=1,
            page_end=1,
        )
    ]
    enriched_elements = [
        CanonicalElement(
            element_id="canon_002",
            document_id="doc_placeholder",
            element_type=ElementType.TEXT,
            text="OCR fallback text",
            order_index=1,
            page_start=1,
            page_end=1,
        )
    ]
    workflow = ParsingWorkflow(
        parser=FakeParser(raw_parsed_document),
        normalizer=FakeNormalizer(canonical_elements),
        document_graph_builder=FakeGraphBuilder(sample_document_graph),
        id_generator=IdGenerator(),
        page_ocr_fallback_workflow=FakePageOCRFallbackWorkflow(enriched_elements),
    )

    workflow.parse(
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
        content_hash="content_hash_001",
    )

    assert workflow.page_ocr_fallback_workflow.calls == [
        ("data/input/pump_manual.pdf", 2)
    ]
    assert workflow.document_graph_builder.calls[0]["canonical_elements"] == enriched_elements
