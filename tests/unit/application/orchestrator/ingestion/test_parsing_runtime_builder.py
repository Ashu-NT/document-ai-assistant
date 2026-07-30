from __future__ import annotations

from dataclasses import dataclass

from src.application.orchestrator.ingestion import parsing_runtime_builder
from src.shared.ids import IdGenerator


class _FakeParser:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeNormalizer:
    pass


class _FakeGraphValidator:
    pass


class _FakeSectionBuilder:
    def __init__(self, id_generator):
        self.id_generator = id_generator


class _FakeDocumentGraphBuilder:
    def __init__(
        self,
        *,
        id_generator,
        section_builder,
        max_chunk_tokens,
        chunk_overlap,
        min_section_text_length,
        chunk_cross_reference_linker=None,
    ):
        self.id_generator = id_generator
        self.section_builder = section_builder
        self.max_chunk_tokens = max_chunk_tokens
        self.chunk_overlap = chunk_overlap
        self.min_section_text_length = min_section_text_length
        self.chunk_cross_reference_linker = chunk_cross_reference_linker
        self.chunk_builder = object()


@dataclass
class _FakeOcrRuntime:
    policy: object | None = None
    canonical_element_ocr_enricher: object | None = None
    page_ocr_fallback_workflow: object | None = None


@dataclass
class _FakeInputLimits:
    max_file_size_bytes: int
    max_pdf_pages: int
    parse_timeout_seconds: int


@dataclass
class _FakeChunkingSettings:
    max_chunk_tokens: int
    chunk_overlap: int
    min_section_text_length: int


def _patch_construction(monkeypatch, *, ocr_runtime: _FakeOcrRuntime) -> None:
    monkeypatch.setattr(
        parsing_runtime_builder,
        "build_parsing_ocr_runtime",
        lambda *, id_generator: ocr_runtime,
    )
    monkeypatch.setattr(parsing_runtime_builder, "SectionBuilder", _FakeSectionBuilder)
    monkeypatch.setattr(
        parsing_runtime_builder, "DocumentGraphBuilder", _FakeDocumentGraphBuilder
    )
    monkeypatch.setattr(parsing_runtime_builder, "DoclingParser", _FakeParser)
    monkeypatch.setattr(
        parsing_runtime_builder, "DoclingDocumentNormalizer", _FakeNormalizer
    )
    monkeypatch.setattr(parsing_runtime_builder, "DocumentGraphValidator", _FakeGraphValidator)
    monkeypatch.setattr(
        parsing_runtime_builder,
        "resolve_ingestion_input_limits",
        lambda: _FakeInputLimits(
            max_file_size_bytes=2048,
            max_pdf_pages=12,
            parse_timeout_seconds=600,
        ),
    )
    monkeypatch.setattr(
        parsing_runtime_builder,
        "resolve_parsing_chunking_settings",
        lambda: _FakeChunkingSettings(
            max_chunk_tokens=700,
            chunk_overlap=70,
            min_section_text_length=90,
        ),
    )


def test_build_parsing_runtime_wires_parsing_workflow(monkeypatch):
    fake_ocr_runtime = _FakeOcrRuntime(
        policy="policy",
        canonical_element_ocr_enricher="enricher",
        page_ocr_fallback_workflow="fallback",
    )
    _patch_construction(monkeypatch, ocr_runtime=fake_ocr_runtime)

    id_generator = IdGenerator()
    parsing_workflow, document_graph_builder = parsing_runtime_builder.build_parsing_runtime(
        id_generator=id_generator,
    )

    assert isinstance(document_graph_builder, _FakeDocumentGraphBuilder)
    assert document_graph_builder.id_generator is id_generator
    assert isinstance(document_graph_builder.section_builder, _FakeSectionBuilder)
    assert document_graph_builder.max_chunk_tokens == 700
    assert document_graph_builder.chunk_overlap == 70
    assert document_graph_builder.min_section_text_length == 90

    assert isinstance(parsing_workflow.parser, _FakeParser)
    assert parsing_workflow.parser.kwargs == {
        "max_num_pages": 12,
        "max_file_size_bytes": 2048,
        "timeout_seconds": 600,
    }
    assert isinstance(parsing_workflow.normalizer, _FakeNormalizer)
    assert isinstance(parsing_workflow.document_graph_validator, _FakeGraphValidator)
    assert parsing_workflow.document_graph_builder is document_graph_builder
    assert parsing_workflow.id_generator is id_generator
    assert parsing_workflow.ocr_policy == "policy"
    assert parsing_workflow.canonical_element_ocr_enricher == "enricher"
    assert parsing_workflow.page_ocr_fallback_workflow == "fallback"


def test_build_parsing_runtime_passes_none_ocr_hooks_when_ocr_disabled(monkeypatch):
    fake_ocr_runtime = _FakeOcrRuntime()
    _patch_construction(monkeypatch, ocr_runtime=fake_ocr_runtime)

    parsing_workflow, _ = parsing_runtime_builder.build_parsing_runtime(
        id_generator=IdGenerator(),
    )

    assert parsing_workflow.canonical_element_ocr_enricher is None
    assert parsing_workflow.page_ocr_fallback_workflow is None
