from __future__ import annotations

from pathlib import Path

import pytest
from docling_core.types.doc import DocItemLabel, DoclingDocument, GroupLabel
from docling_core.types.doc.base import Size

from src.application.evaluation.golden.cache_only_parser_guard import (
    CacheOnlyParserGuard,
    GoldenCorpusDoclingUnavailableError,
)
from src.application.validation.common import ValidationResult
from src.application.workflows.parsing import ParsedCanonicalElement, ParsingWorkflow
from src.application.workflows.parsing.builders.document_graph_build_result import (
    DocumentGraphBuildResult,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import ElementType
from src.infrastructure.parsing.artifact_store.filesystem_parsed_artifact_store import (
    FilesystemParsedArtifactStore,
)
from src.shared.ids import IdGenerator


def _build_docling_document(marker: str) -> DoclingDocument:
    doc = DoclingDocument(name=marker)
    doc.add_page(page_no=1, size=Size(width=612.0, height=792.0))
    doc.add_heading(text=f"{marker} heading", level=1)
    group = doc.add_group(label=GroupLabel.LIST, name=f"{marker}-list")
    doc.add_text(label=DocItemLabel.LIST_ITEM, text=f"{marker} item", parent=group)
    return doc


class RealParser:
    """Mirrors `DoclingParser`'s contract: a real `parser_version` attribute
    plus `resolve_conversion_fingerprint`. `CacheOnlyParserGuard` wraps an
    instance of this, exactly like the production CORE-document parsing
    workflow in the golden-evaluation scripts."""

    parser_name = "docling"

    def __init__(self, raw_parsed_document: RawParsedDocument, *, parser_version: str) -> None:
        self.parser_version = parser_version
        self.raw_parsed_document = raw_parsed_document
        self.calls: list[str] = []

    def parse(self, file_path: str, *, enable_ocr_override: bool | None = None) -> RawParsedDocument:
        self.calls.append(file_path)
        return self.raw_parsed_document

    def resolve_conversion_fingerprint(self, *, enable_ocr_override: bool | None = None) -> str:
        return "fp-1"


class FakeNormalizer:
    def __init__(self, canonical_elements: list[ParsedCanonicalElement]) -> None:
        self.canonical_elements = canonical_elements

    def normalize(self, raw_parsed_document, document_id, *, skipped_item_errors=None):
        return self.canonical_elements


class FakeDocumentGraphBuilder:
    def __init__(self, document_graph) -> None:
        self.document_graph = document_graph

    def build(self, **kwargs):
        return DocumentGraphBuildResult(
            graph=self.document_graph, cross_reference_linking_outcome=None
        )


class SpyDocumentGraphValidator:
    def validate(self, value):
        return ValidationResult()


def _build_raw_parsed_document(marker: str, *, parser_version: str) -> RawParsedDocument:
    return RawParsedDocument(
        file_path=f"data/input/{marker}.pdf",
        title=f"{marker} title",
        page_count=1,
        raw_document=_build_docling_document(marker),
        parser_name="docling",
        parser_version=parser_version,
    )


def _build_cache_only_workflow(
    *, real_parser: RealParser, parsed_artifact_store, sample_document_graph
) -> ParsingWorkflow:
    canonical_elements = [
        ParsedCanonicalElement(
            element_id="canon_001",
            document_id="doc_placeholder",
            element_type=ElementType.TEXT,
            text="content",
            order_index=1,
        )
    ]
    return ParsingWorkflow(
        parser=CacheOnlyParserGuard(real_parser),
        normalizer=FakeNormalizer(canonical_elements),
        document_graph_builder=FakeDocumentGraphBuilder(sample_document_graph),
        id_generator=IdGenerator(),
        document_graph_validator=SpyDocumentGraphValidator(),
        parsed_artifact_store=parsed_artifact_store,
    )


class TestCacheOnlyParserGuardDirectly:
    def test_parse_always_raises_without_touching_real_docling(self) -> None:
        real_parser = RealParser(
            _build_raw_parsed_document("DIRECT", parser_version="2.126.0"),
            parser_version="2.126.0",
        )
        guard = CacheOnlyParserGuard(real_parser)

        with pytest.raises(GoldenCorpusDoclingUnavailableError):
            guard.parse("data/input/any.pdf")

        assert real_parser.calls == []  # real Docling conversion never invoked


class TestCacheOnlyModeAgainstRealCacheMechanism:
    """Reproduces, at the `ParsingWorkflow` level, the exact failure found
    in this investigation: a cached artifact published under one Docling
    `parser_version` is unreachable from cache-only mode once the active
    environment's installed parser reports a different version - even
    though the artifact is present, uncorrupted, and otherwise identical."""

    def test_cache_hit_when_parser_version_matches_published_artifact(
        self, tmp_path: Path, sample_document_graph
    ) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        publishing_parser = RealParser(
            _build_raw_parsed_document("MATCH", parser_version="2.126.0"),
            parser_version="2.126.0",
        )
        publishing_workflow = _build_cache_only_workflow(
            real_parser=RealParser(
                publishing_parser.raw_parsed_document, parser_version="2.126.0"
            ),
            parsed_artifact_store=store,
            sample_document_graph=sample_document_graph,
        )
        # Publish directly (bypassing the guard) - this is what a real
        # Docling run did at some point in the past, outside cache-only mode.
        from src.application.workflows.parsing.artifact_store.parsed_artifact_key import (
            ParsedArtifactKey,
        )

        store.put(
            ParsedArtifactKey(
                source_sha256="hash-1",
                parser_name="docling",
                parser_version="2.126.0",
                conversion_fingerprint="fp-1",
            ),
            publishing_parser.raw_parsed_document,
        )

        result = publishing_workflow.parse(
            file_path="data/input/manual.pdf",
            file_hash="hash-1",
            content_hash=None,
            document_id="doc_1",
        )

        assert result.document_graph is not None

    def test_cache_miss_raises_unavailable_error_when_parser_version_drifts(
        self, tmp_path: Path, sample_document_graph
    ) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        from src.application.workflows.parsing.artifact_store.parsed_artifact_key import (
            ParsedArtifactKey,
        )

        store.put(
            ParsedArtifactKey(
                source_sha256="hash-1",
                parser_name="docling",
                parser_version="2.126.0",
                conversion_fingerprint="fp-1",
            ),
            _build_raw_parsed_document("DRIFTED", parser_version="2.126.0"),
        )

        drifted_real_parser = RealParser(
            _build_raw_parsed_document("DRIFTED", parser_version="2.111.0"),
            parser_version="2.111.0",
        )
        drifted_workflow = _build_cache_only_workflow(
            real_parser=drifted_real_parser,
            parsed_artifact_store=store,
            sample_document_graph=sample_document_graph,
        )

        with pytest.raises(GoldenCorpusDoclingUnavailableError):
            drifted_workflow.parse(
                file_path="data/input/manual.pdf",
                file_hash="hash-1",
                content_hash=None,
                document_id="doc_1",
            )

        # The guard raised instead of silently invoking real Docling
        # conversion - integrity/compatibility validation was never
        # bypassed, and no unsafe fallback occurred.
        assert drifted_real_parser.calls == []
