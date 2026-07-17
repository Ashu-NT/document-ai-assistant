from __future__ import annotations

from dataclasses import dataclass

from src.application.orchestrator.ingestion import parsing_runtime_builder
from src.shared.ids import IdGenerator


class _FakeParser:
    pass


class _FakeNormalizer:
    pass


class _FakeGraphValidator:
    pass


class _FakeSectionBuilder:
    def __init__(self, id_generator):
        self.id_generator = id_generator


class _FakeDocumentGraphBuilder:
    def __init__(self, *, id_generator, section_builder):
        self.id_generator = id_generator
        self.section_builder = section_builder
        self.chunk_builder = object()


@dataclass
class _FakeOcrRuntime:
    policy: object | None = None
    canonical_element_ocr_enricher: object | None = None
    page_ocr_fallback_workflow: object | None = None


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

    assert isinstance(parsing_workflow.parser, _FakeParser)
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
