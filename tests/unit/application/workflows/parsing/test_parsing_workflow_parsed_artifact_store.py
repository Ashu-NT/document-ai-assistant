from __future__ import annotations

import copy
from pathlib import Path

from docling_core.types.doc import DocItemLabel, DoclingDocument, GroupLabel
from docling_core.types.doc.base import Size

from src.application.validation.common import ValidationResult
from src.application.workflows.parsing import (
    ParsedCanonicalElement,
    ParsingWorkflow,
    RawParsedDocument,
)
from src.application.workflows.parsing.builders.document_graph_build_result import (
    DocumentGraphBuildResult,
)
from src.domain.common import ElementType
from src.infrastructure.parsing.artifact_store.filesystem_parsed_artifact_store import (
    FilesystemParsedArtifactStore,
)
from src.shared.exceptions import ArtifactStoreError
from src.shared.ids import IdGenerator


def _build_docling_document(marker: str) -> DoclingDocument:
    doc = DoclingDocument(name=marker)
    doc.add_page(page_no=1, size=Size(width=612.0, height=792.0))
    doc.add_heading(text=f"{marker} heading", level=1)
    group = doc.add_group(label=GroupLabel.LIST, name=f"{marker}-list")
    doc.add_text(label=DocItemLabel.LIST_ITEM, text=f"{marker} item", parent=group)
    return doc


class FakeParser:
    parser_name = "docling"
    parser_version = "1.2.3"

    def __init__(self, raw_parsed_document: RawParsedDocument) -> None:
        self.raw_parsed_document = raw_parsed_document
        self.calls: list[str] = []
        self.enable_ocr_overrides: list[bool | None] = []
        self.fingerprint_calls: list[bool | None] = []

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
        self.calls.append(file_path)
        self.enable_ocr_overrides.append(enable_ocr_override)
        return self.raw_parsed_document

    def resolve_conversion_fingerprint(
        self,
        *,
        enable_ocr_override: bool | None = None,
    ) -> str:
        self.fingerprint_calls.append(enable_ocr_override)
        return f"fp-ocr={enable_ocr_override}"


class FakeParserWithoutFingerprint:
    """Mirrors every existing fake parser in this test suite: no
    `resolve_conversion_fingerprint`, matching every parser built before the
    parsed-artifact-store feature existed."""

    parser_name = "docling"
    parser_version = "1.2.3"

    def __init__(self, raw_parsed_document: RawParsedDocument) -> None:
        self.raw_parsed_document = raw_parsed_document
        self.calls: list[str] = []

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
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
        *,
        skipped_item_errors: list[str] | None = None,
    ) -> list[ParsedCanonicalElement]:
        self.calls.append((raw_parsed_document, document_id))
        return self.canonical_elements


class FakeDocumentGraphBuilder:
    def __init__(self, document_graph) -> None:
        self.document_graph = document_graph
        self.calls: list[dict] = []

    def build(self, **kwargs):
        self.calls.append(kwargs)
        return DocumentGraphBuildResult(
            graph=self.document_graph,
            cross_reference_linking_outcome=None,
        )


class SpyDocumentGraphValidator:
    def __init__(self) -> None:
        self.calls = []

    def validate(self, value):
        self.calls.append(value)
        return ValidationResult()


class FailingArtifactStore:
    def get(self, key, *, file_path):
        return None

    def put(self, key, document) -> None:
        raise ArtifactStoreError("simulated publish failure")


def _build_raw_parsed_document(marker: str, *, file_path: str) -> RawParsedDocument:
    return RawParsedDocument(
        file_path=file_path,
        title=f"{marker} title",
        page_count=1,
        raw_document=_build_docling_document(marker),
        parser_name="docling",
        parser_version="1.2.3",
    )


def _build_workflow(
    *,
    parser,
    sample_document_graph,
    parsed_artifact_store=None,
) -> tuple[ParsingWorkflow, FakeDocumentGraphBuilder]:
    canonical_elements = [
        ParsedCanonicalElement(
            element_id="canon_001",
            document_id="doc_placeholder",
            element_type=ElementType.TEXT,
            text="content",
            order_index=1,
        )
    ]
    graph_builder = FakeDocumentGraphBuilder(copy.deepcopy(sample_document_graph))
    workflow = ParsingWorkflow(
        parser=parser,
        normalizer=FakeNormalizer(canonical_elements),
        document_graph_builder=graph_builder,
        id_generator=IdGenerator(),
        document_graph_validator=SpyDocumentGraphValidator(),
        parsed_artifact_store=parsed_artifact_store,
    )
    return workflow, graph_builder


def test_second_parse_of_same_document_is_served_from_cache(
    tmp_path: Path, sample_document_graph
) -> None:
    store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
    raw_parsed_document = _build_raw_parsed_document(
        "CACHE", file_path="data/input/manual.pdf"
    )
    parser = FakeParser(raw_parsed_document)
    workflow, _ = _build_workflow(
        parser=parser,
        sample_document_graph=sample_document_graph,
        parsed_artifact_store=store,
    )

    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_1",
    )
    assert len(parser.calls) == 1

    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_2",
    )
    assert len(parser.calls) == 1  # served from cache, Docling not re-invoked


def test_different_enable_ocr_override_misses_cache_independently(
    tmp_path: Path, sample_document_graph
) -> None:
    store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
    raw_parsed_document = _build_raw_parsed_document(
        "OCR", file_path="data/input/manual.pdf"
    )
    parser = FakeParser(raw_parsed_document)
    workflow, _ = _build_workflow(
        parser=parser,
        sample_document_graph=sample_document_graph,
        parsed_artifact_store=store,
    )

    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_1",
        enable_ocr_override=True,
    )
    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_2",
        enable_ocr_override=False,
    )

    assert len(parser.calls) == 2  # different conversion configuration, both misses


def test_failed_publication_does_not_fail_parsing(
    sample_document_graph,
) -> None:
    raw_parsed_document = _build_raw_parsed_document(
        "PUBFAIL", file_path="data/input/manual.pdf"
    )
    parser = FakeParser(raw_parsed_document)
    workflow, _ = _build_workflow(
        parser=parser,
        sample_document_graph=sample_document_graph,
        parsed_artifact_store=FailingArtifactStore(),
    )

    result = workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_1",
    )

    assert result.document_graph is not None
    assert len(parser.calls) == 1


def test_no_store_configured_leaves_behavior_unchanged(
    sample_document_graph,
) -> None:
    raw_parsed_document = _build_raw_parsed_document(
        "NOSTORE", file_path="data/input/manual.pdf"
    )
    parser = FakeParserWithoutFingerprint(raw_parsed_document)
    workflow, _ = _build_workflow(
        parser=parser,
        sample_document_graph=sample_document_graph,
        parsed_artifact_store=None,
    )

    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_1",
    )
    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_2",
    )

    assert len(parser.calls) == 2  # no caching at all: parser invoked every time


def test_store_configured_but_parser_lacks_fingerprint_support_is_ignored(
    tmp_path: Path, sample_document_graph
) -> None:
    store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
    raw_parsed_document = _build_raw_parsed_document(
        "NOFP", file_path="data/input/manual.pdf"
    )
    parser = FakeParserWithoutFingerprint(raw_parsed_document)
    workflow, _ = _build_workflow(
        parser=parser,
        sample_document_graph=sample_document_graph,
        parsed_artifact_store=store,
    )

    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_1",
    )
    workflow.parse(
        file_path="data/input/manual.pdf",
        file_hash="hash-1",
        content_hash=None,
        document_id="doc_2",
    )

    assert len(parser.calls) == 2  # caching silently skipped, parsing unaffected
