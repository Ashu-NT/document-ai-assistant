from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.application.evaluation.classification.golden_classification_runner import (
    FRESH_MODEL_EXECUTION_MODE,
    run_classification_golden_evaluation,
)
from src.application.evaluation.classification.golden_classification_document_result import (
    ClassificationStageStatus,
)
from src.application.evaluation.corpus import GoldenCorpusManifest, GoldenDocumentManifestEntry
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationStatus,
)
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes


def _make_document_graph(alias: str) -> DocumentGraph:
    document = Document(
        document_id=f"doc_{alias}",
        file_name=f"{alias}.pdf",
        file_path=f"{alias}.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=DocumentType.MANUAL,
    )
    return DocumentGraph(document=document)


def _write_dummy_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.4 dummy")


class FakeParser:
    parser_name = "fake"
    parser_version = "1.0"

    def resolve_conversion_fingerprint(self, *, enable_ocr_override=None) -> str:
        return "fake-fp"


class FakeParsingWorkflow:
    def __init__(self, graphs_by_path: dict[str, DocumentGraph]) -> None:
        self.parser = FakeParser()
        self._graphs_by_path = graphs_by_path
        self.parse_calls: list[str] = []

    def parse(self, *, file_path, file_hash, content_hash, document_id):
        self.parse_calls.append(file_path)
        return SimpleNamespace(document_graph=self._graphs_by_path[file_path])


class FakeClassificationWorkflow:
    """Stands in for DocumentClassificationWorkflow. Records every call so
    tests can prove classify_document_attempt() is what gets invoked
    (never classify_document()), and can be configured per document_id to
    raise (simulating an execution failure) or return a canned
    classification."""

    classification_model = "fake-model"

    def __init__(
        self,
        classifications_by_document_id: dict[str, DocumentClassification],
        *,
        raise_for_document_ids: frozenset[str] = frozenset(),
    ) -> None:
        self._classifications = classifications_by_document_id
        self._raise_for = raise_for_document_ids
        self.attempt_calls: list[str] = []

    def classify_document_attempt(self, document_graph, activity_context=None):
        document_id = document_graph.document.document_id
        self.attempt_calls.append(document_id)
        if document_id in self._raise_for:
            raise RuntimeError(f"LLM unavailable for {document_id}")
        return self._classifications[document_id]


def _classification(document_id: str, *, document_type: DocumentType, confidence: float) -> DocumentClassification:
    return DocumentClassification(
        document_id=document_id,
        document_type=document_type,
        result=ClassificationResult(
            classification_id=f"classification_{document_id}",
            document_id=document_id,
            predicted_label=document_type.value,
            confidence_score=confidence,
            rationale="fake",
            evidence=[],
        ),
    )


class TestBasicExecution:
    def test_evaluates_available_documents_with_fresh_classification_attempts(
        self, tmp_path, monkeypatch
    ) -> None:
        from src.config.settings import golden_corpus_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        graph = _make_document_graph("doc_a")
        parsing_workflow = FakeParsingWorkflow({str(tmp_path / "a.pdf"): graph})
        classification_workflow = FakeClassificationWorkflow(
            {"doc_doc_a": _classification("doc_doc_a", document_type=DocumentType.MANUAL, confidence=0.95)}
        )

        report = run_classification_golden_evaluation(
            manifest=manifest,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
        )

        assert len(report.classification_results) == 1
        result = report.classification_results[0]
        assert result.alias == "doc_a"
        assert result.stage_status == ClassificationStageStatus.EVALUATED
        assert result.attempt is not None
        assert result.attempt.predicted_document_type == DocumentType.MANUAL
        assert classification_workflow.attempt_calls == ["doc_doc_a"]

    def test_skips_classification_when_parsing_is_unavailable(self, tmp_path, monkeypatch) -> None:
        from src.config.settings import golden_corpus_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_missing", relative_path="missing.pdf", category="manual")],
            root_dir=tmp_path,
        )
        parsing_workflow = FakeParsingWorkflow({})
        classification_workflow = FakeClassificationWorkflow({})

        report = run_classification_golden_evaluation(
            manifest=manifest,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
        )

        assert report.document_outcomes[0].status == GoldenDocumentEvaluationStatus.CORPUS_MISSING
        result = report.classification_results[0]
        assert result.stage_status == ClassificationStageStatus.SKIPPED_PARSING_UNAVAILABLE
        assert classification_workflow.attempt_calls == []  # never even attempted

    def test_execution_failure_for_one_document_does_not_abort_the_batch(
        self, tmp_path, monkeypatch
    ) -> None:
        from src.config.settings import golden_corpus_settings

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
        graph_a = _make_document_graph("doc_a")
        graph_b = _make_document_graph("doc_b")
        parsing_workflow = FakeParsingWorkflow(
            {
                str(tmp_path / "a.pdf"): graph_a,
                str(tmp_path / "b.pdf"): graph_b,
            }
        )
        classification_workflow = FakeClassificationWorkflow(
            {"doc_doc_b": _classification("doc_doc_b", document_type=DocumentType.MANUAL, confidence=0.95)},
            raise_for_document_ids=frozenset({"doc_doc_a"}),
        )

        report = run_classification_golden_evaluation(
            manifest=manifest,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
        )

        by_alias = {r.alias: r for r in report.classification_results}
        assert by_alias["doc_a"].stage_status == ClassificationStageStatus.EXECUTION_FAILED
        assert "doc_doc_a" in (by_alias["doc_a"].execution_error or "")
        assert by_alias["doc_b"].stage_status == ClassificationStageStatus.EVALUATED

    def test_fresh_model_mode_ignores_reclassification_and_cache_settings(
        self, tmp_path, monkeypatch
    ) -> None:
        from src.config.settings import golden_corpus_settings, classification_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))
        monkeypatch.setattr(classification_settings, "allow_reclassification", False)
        monkeypatch.setattr(classification_settings, "use_cache", True)
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        graph = _make_document_graph("doc_a")
        parsing_workflow = FakeParsingWorkflow({str(tmp_path / "a.pdf"): graph})
        classification_workflow = FakeClassificationWorkflow(
            {"doc_doc_a": _classification("doc_doc_a", document_type=DocumentType.MANUAL, confidence=0.95)}
        )

        report = run_classification_golden_evaluation(
            manifest=manifest,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
        )

        # Structural guarantee: classify_document_attempt() was still called
        # even though production settings say "don't reclassify, use cache" -
        # this runner never even reads those settings to decide whether to
        # call the LLM, it only RECORDS them for reproducibility.
        assert classification_workflow.attempt_calls == ["doc_doc_a"]
        assert report.run_metadata.classification_execution_mode == FRESH_MODEL_EXECUTION_MODE
        assert report.run_metadata.classification_allow_reclassification is False
        assert report.run_metadata.classification_use_cache is True
        assert report.run_metadata.classification_model == "fake-model"

    def test_confidence_threshold_override_is_used_and_recorded(self, tmp_path, monkeypatch) -> None:
        from src.config.settings import golden_corpus_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        graph = _make_document_graph("doc_a")
        parsing_workflow = FakeParsingWorkflow({str(tmp_path / "a.pdf"): graph})
        classification_workflow = FakeClassificationWorkflow(
            {"doc_doc_a": _classification("doc_doc_a", document_type=DocumentType.MANUAL, confidence=0.5)}
        )

        report = run_classification_golden_evaluation(
            manifest=manifest,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
            confidence_threshold=0.9,
        )

        result = report.classification_results[0]
        assert result.attempt is not None
        assert result.attempt.passed_confidence_gate is False
        assert report.run_metadata.classification_confidence_threshold == 0.9

    def test_parsing_stage_document_outcomes_never_carry_structural_results(
        self, tmp_path, monkeypatch
    ) -> None:
        # Phase 1's structural/cross-reference/chunk-budget evaluation stays
        # untouched by this classification-only runner.
        from src.config.settings import golden_corpus_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        graph = _make_document_graph("doc_a")
        parsing_workflow = FakeParsingWorkflow({str(tmp_path / "a.pdf"): graph})
        classification_workflow = FakeClassificationWorkflow(
            {"doc_doc_a": _classification("doc_doc_a", document_type=DocumentType.MANUAL, confidence=0.95)}
        )

        report = run_classification_golden_evaluation(
            manifest=manifest,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
        )

        outcome = report.document_outcomes[0]
        assert outcome.structural_result is None
        assert outcome.cross_reference_result is None
        assert outcome.chunk_token_budget_result is None


class TestExpectationAttachment:
    def test_expectation_is_attached_by_alias_when_fixture_provided(
        self, tmp_path, monkeypatch
    ) -> None:
        from src.config.settings import golden_corpus_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        expectations_path = tmp_path / "classification_expectations.md"
        expectations_path.write_text(
            """
# 1. Classification Expectations

```yaml
document_alias: doc_a
expected_document_type: manual
review_status: reviewed
```
""",
            encoding="utf-8",
        )
        graph = _make_document_graph("doc_a")
        parsing_workflow = FakeParsingWorkflow({str(tmp_path / "a.pdf"): graph})
        classification_workflow = FakeClassificationWorkflow(
            {"doc_doc_a": _classification("doc_doc_a", document_type=DocumentType.MANUAL, confidence=0.95)}
        )

        report = run_classification_golden_evaluation(
            manifest=manifest,
            expectation_cases_path=expectations_path,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
        )

        result = report.classification_results[0]
        assert result.expectation is not None
        assert result.expectation.expected_document_type == DocumentType.MANUAL
        assert result.eligible_for_accuracy is True
        assert result.raw_prediction_correct is True

    def test_no_fixture_file_leaves_expectation_none_not_an_error(
        self, tmp_path, monkeypatch
    ) -> None:
        from src.config.settings import golden_corpus_settings

        monkeypatch.setattr(golden_corpus_settings, "root_dir", str(tmp_path))
        _write_dummy_pdf(tmp_path / "a.pdf")
        manifest = GoldenCorpusManifest(
            [GoldenDocumentManifestEntry(alias="doc_a", relative_path="a.pdf", category="manual")],
            root_dir=tmp_path,
        )
        graph = _make_document_graph("doc_a")
        parsing_workflow = FakeParsingWorkflow({str(tmp_path / "a.pdf"): graph})
        classification_workflow = FakeClassificationWorkflow(
            {"doc_doc_a": _classification("doc_doc_a", document_type=DocumentType.MANUAL, confidence=0.95)}
        )

        report = run_classification_golden_evaluation(
            manifest=manifest,
            parsing_workflow=parsing_workflow,
            classification_workflow=classification_workflow,
        )

        result = report.classification_results[0]
        assert result.expectation is None
        assert result.eligible_for_accuracy is False
