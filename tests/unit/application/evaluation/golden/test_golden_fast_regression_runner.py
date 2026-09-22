from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from docling_core.types.doc import DocItemLabel, DoclingDocument, GroupLabel
from docling_core.types.doc.base import Size

from src.application.evaluation.corpus import (
    GoldenCorpusManifest,
    GoldenDocumentManifestEntry,
)
from src.application.evaluation.golden import (
    GoldenDocumentEvaluationStatus,
    run_fast_golden_regression,
)
from src.application.validation.common import ValidationResult
from src.application.workflows.parsing import ParsingWorkflow, RawParsedDocument
from src.application.workflows.parsing.builders.document_graph_build_result import (
    DocumentGraphBuildResult,
)
from src.domain.common import DocumentType
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes
from src.infrastructure.parsing.artifact_store.filesystem_parsed_artifact_store import (
    FilesystemParsedArtifactStore,
)
from src.shared.ids import IdGenerator


def _make_document_graph(alias: str) -> DocumentGraph:
    document = Document(
        document_id=f"doc_{alias}",
        file_name=f"{alias}.pdf",
        file_path=f"{alias}.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=DocumentType.MANUAL,
    )
    return DocumentGraph(document=document)


class FakeParser:
    parser_name = "fake"
    parser_version = "1.0"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def resolve_conversion_fingerprint(self, *, enable_ocr_override=None) -> str:
        return "fake-fp"


class FakeParsingWorkflow:
    """Bare fake used where the test only cares about the RUNNER's own
    outcome/coverage bookkeeping, not real cache-check-then-parse
    semantics (see FilesystemParsedArtifactStore-backed tests below for
    that)."""

    def __init__(self, graphs_by_path: dict[str, DocumentGraph]) -> None:
        self.parser = FakeParser()
        self._graphs_by_path = graphs_by_path
        self.parse_calls: list[str] = []

    def parse(self, *, file_path, file_hash, content_hash, document_id):
        self.parse_calls.append(file_path)
        return SimpleNamespace(document_graph=self._graphs_by_path[file_path])


def _write_dummy_pdf(path: Path, content: bytes = b"%PDF-1.4 dummy") -> None:
    path.write_bytes(content)


class TestCoverageAndOutcomes:
    def test_evaluates_available_documents_and_reports_coverage(
        self, tmp_path, monkeypatch
    ) -> None:
        from src.config.settings import golden_corpus_settings

        # Isolate from any real TestDoc/fixtures/*.md on this machine - this
        # test only cares about coverage bookkeeping, not curated cases.
        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))

        _write_dummy_pdf(tmp_path / "a.pdf")
        _write_dummy_pdf(tmp_path / "b.pdf")
        manifest = GoldenCorpusManifest(
            [
                GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual"),
                GoldenDocumentManifestEntry(alias="doc_b", relative_path="b.pdf", category="manual"),
            ],
            root_dir=tmp_path,
        )
        graphs_by_path = {
            str(tmp_path / "a.pdf"): _make_document_graph("doc_a"),
            str(tmp_path / "b.pdf"): _make_document_graph("doc_b"),
        }
        workflow = FakeParsingWorkflow(graphs_by_path)

        report = run_fast_golden_regression(manifest=manifest, parsing_workflow=workflow)

        assert report.corpus_coverage.expected == 2
        assert report.corpus_coverage.available == 2
        assert report.corpus_coverage.evaluated == 2
        assert {o.alias for o in report.document_outcomes} == {"doc_a", "doc_b"}
        assert all(o.was_evaluated for o in report.document_outcomes)

    def test_missing_document_is_explicit_not_silently_skipped(self, tmp_path) -> None:
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [
                GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual"),
                GoldenDocumentManifestEntry(
                    alias="doc_missing", relative_path="missing.pdf", category="manual"
                ),
            ],
            root_dir=tmp_path,
        )
        graphs_by_path = {str(tmp_path / "a.pdf"): _make_document_graph("doc_a")}
        workflow = FakeParsingWorkflow(graphs_by_path)

        report = run_fast_golden_regression(manifest=manifest, parsing_workflow=workflow)

        assert report.corpus_coverage.expected == 2
        assert report.corpus_coverage.available == 1
        assert report.corpus_coverage.evaluated == 1
        assert report.corpus_coverage.missing_aliases == ("doc_missing",)

        missing_outcome = next(
            o for o in report.document_outcomes if o.alias == "doc_missing"
        )
        assert missing_outcome.status == GoldenDocumentEvaluationStatus.CORPUS_MISSING
        assert missing_outcome.was_evaluated is False
        assert missing_outcome in report.documents_not_evaluated

    def test_hash_mismatch_is_explicit(self, tmp_path) -> None:
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [
                GoldenDocumentManifestEntry(
                    alias="doc_a",
                    relative_path="a.pdf",
                    category="manual",
                    expected_sha256="0" * 64,
                ),
            ],
            root_dir=tmp_path,
        )
        workflow = FakeParsingWorkflow({})

        report = run_fast_golden_regression(manifest=manifest, parsing_workflow=workflow)

        assert report.corpus_coverage.available == 0
        assert report.corpus_coverage.evaluated == 0
        assert report.corpus_coverage.hash_mismatch_aliases == ("doc_a",)
        outcome = report.document_outcomes[0]
        assert outcome.status == GoldenDocumentEvaluationStatus.CORPUS_HASH_MISMATCH
        assert workflow.parse_calls == []  # never even attempted to parse

    def test_unavailable_corpus_does_not_masquerade_as_successful_full_run(
        self, tmp_path
    ) -> None:
        manifest = GoldenCorpusManifest(
            [
                GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual"),
                GoldenDocumentManifestEntry(alias="doc_b", relative_path="b.pdf", category="manual"),
            ],
            root_dir=tmp_path,
        )
        workflow = FakeParsingWorkflow({})

        report = run_fast_golden_regression(manifest=manifest, parsing_workflow=workflow)

        assert report.corpus_coverage.expected == 2
        assert report.corpus_coverage.available == 0
        assert report.corpus_coverage.evaluated == 0
        assert len(report.documents_not_evaluated) == 2
        # A caller checking "did everything pass" must be able to see this
        # was NOT a real successful evaluation of the corpus.
        assert report.structural_passed_count == 0


class _FakeNormalizer:
    def normalize(self, raw_parsed_document, document_id, *, skipped_item_errors=None):
        return []


class _FakeDocumentGraphBuilder:
    def __init__(self, graph: DocumentGraph) -> None:
        self.graph = graph

    def build(self, **kwargs):
        return DocumentGraphBuildResult(graph=self.graph, cross_reference_linking_outcome=None)


class _SpyValidator:
    def validate(self, value):
        return ValidationResult()


def _build_real_docling_document(marker: str) -> DoclingDocument:
    doc = DoclingDocument(name=marker)
    doc.add_page(page_no=1, size=Size(width=612.0, height=792.0))
    doc.add_heading(text=f"{marker} heading", level=1)
    group = doc.add_group(label=GroupLabel.LIST, name=f"{marker}-list")
    doc.add_text(label=DocItemLabel.LIST_ITEM, text=f"{marker} item", parent=group)
    return doc


class FakeCacheableParser:
    parser_name = "docling"
    parser_version = "1.2.3"

    def __init__(self, raw_parsed_document: RawParsedDocument) -> None:
        self.raw_parsed_document = raw_parsed_document
        self.calls: list[str] = []

    def parse(self, file_path, *, enable_ocr_override=None) -> RawParsedDocument:
        self.calls.append(file_path)
        return self.raw_parsed_document

    def resolve_conversion_fingerprint(self, *, enable_ocr_override=None) -> str:
        return "fp-1"


class TestCachedArtifactPath:
    def _build_workflow(self, tmp_path, parser) -> tuple[ParsingWorkflow, object]:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        graph = _make_document_graph("doc_a")
        workflow = ParsingWorkflow(
            parser=parser,
            normalizer=_FakeNormalizer(),
            document_graph_builder=_FakeDocumentGraphBuilder(graph),
            id_generator=IdGenerator(),
            document_graph_validator=_SpyValidator(),
            parsed_artifact_store=store,
        )
        return workflow, store

    def test_cache_miss_in_cached_only_mode_never_calls_underlying_parser(
        self, tmp_path
    ) -> None:
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        raw_parsed_document = RawParsedDocument(
            file_path="a.pdf",
            title="a",
            page_count=1,
            raw_document=_build_real_docling_document("A"),
            parser_name="docling",
            parser_version="1.2.3",
        )
        parser = FakeCacheableParser(raw_parsed_document)
        workflow, _store = self._build_workflow(tmp_path, parser)

        report = run_fast_golden_regression(
            manifest=manifest, parsing_workflow=workflow, allow_real_parsing=False
        )

        outcome = report.document_outcomes[0]
        assert outcome.status == GoldenDocumentEvaluationStatus.CACHE_MISS_IN_CACHED_ONLY_MODE
        assert parser.calls == []  # real Docling conversion never invoked

    def test_second_run_uses_cached_artifact_without_real_parsing(self, tmp_path) -> None:
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        raw_parsed_document = RawParsedDocument(
            file_path="a.pdf",
            title="a",
            page_count=1,
            raw_document=_build_real_docling_document("A"),
            parser_name="docling",
            parser_version="1.2.3",
        )
        parser = FakeCacheableParser(raw_parsed_document)
        workflow, store = self._build_workflow(tmp_path, parser)

        # First run: real parsing allowed, warms the artifact store.
        first_report = run_fast_golden_regression(
            manifest=manifest, parsing_workflow=workflow, allow_real_parsing=True
        )
        assert first_report.document_outcomes[0].was_evaluated
        assert len(parser.calls) == 1

        # Second run: cached-only mode must succeed from the cache alone.
        parser2 = FakeCacheableParser(raw_parsed_document)
        workflow2, _ = self._build_workflow(tmp_path, parser2)
        # Reuse the SAME store the first run populated.
        workflow2.parsed_artifact_store = store

        second_report = run_fast_golden_regression(
            manifest=manifest, parsing_workflow=workflow2, allow_real_parsing=False
        )

        outcome = second_report.document_outcomes[0]
        assert outcome.status == GoldenDocumentEvaluationStatus.EVALUATED
        assert parser2.calls == []  # served entirely from the cache
