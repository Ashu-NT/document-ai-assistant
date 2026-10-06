"""End-to-end deterministic test of `run_extraction_golden_evaluation` driving
the REAL `ExtractionWorkflow` against a hand-built `DocumentGraph`, with a
`CannedResponseLLMService` standing in for the LLM and an in-memory
extraction repository standing in for the database - no network, no real
DB, matching the isolation pattern documented in extraction_isolation.py.
"""

import json

from src.application.evaluation.corpus.evaluation_corpus_tier import (
    EvaluationCorpusTier,
)
from src.application.evaluation.corpus.golden_corpus_manifest import (
    GoldenCorpusManifest,
)
from src.application.evaluation.corpus.golden_document_manifest_entry import (
    GoldenDocumentManifestEntry,
)
from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
)
from src.application.evaluation.extraction.extraction_applicability import (
    ExtractionApplicability,
)
from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractedEvidenceExpectation,
    ExtractionApplicabilityDeclaration,
    ExtractionExpectationCase,
)
from src.application.evaluation.extraction.extraction_isolation import (
    CannedResponseLLMService,
    InMemoryExtractionRepository,
)
from src.application.evaluation.extraction.golden_extraction_document_result import (
    ExtractionStageStatus,
)
from src.application.evaluation.extraction.golden_extraction_runner import (
    run_extraction_golden_evaluation,
)
from src.application.evaluation.extraction.loaders.extraction_expectation_loader import (
    ExtractionTruthSet,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
)
from src.application.services.extraction import ExtractionService
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from src.domain.common import AuditMetadata, SourceLocation
from src.domain.document import DocumentChunk, DocumentGraph
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes
from src.shared.ids import IdGenerator


def _manifest() -> GoldenCorpusManifest:
    return GoldenCorpusManifest(
        entries=(
            GoldenDocumentManifestEntry(
                alias="fake_doc",
                relative_path="fake_doc.pdf",
                category="test",
                tier=EvaluationCorpusTier.CORE,
            ),
        )
    )


def _make_chunk(chunk_id: str, page: int, content: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc1",
        section_id="sec1",
        section_path=["1 Safety"],
        content=content,
        chunk_type="general",
        source=SourceLocation(page_start=page, page_end=page),
        audit=AuditMetadata(),
    )


def _make_graph(chunks: list[DocumentChunk]) -> DocumentGraph:
    document = Document(
        document_id="doc1",
        file_name="fake_doc.pdf",
        file_path="fake_doc.pdf",
        hashes=DocumentHashes(file_hash="deadbeef"),
    )
    return DocumentGraph(
        document=document,
        chunks={chunk.chunk_id: chunk for chunk in chunks},
    )


def _canned_response(**overrides) -> str:
    payload = {
        "confidence_score": 0.9,
        "maintenance_tasks": [],
        "spare_parts": [],
        "equipment": [],
        "manufacturers": [],
        "suppliers": [],
        "contact_points": [],
        "procedures": [],
        "specifications": [],
        "safety_warnings": [],
        "maintenance_intervals": [],
        "troubleshooting_entries": [],
        "identifiers": [],
    }
    payload.update(overrides)
    return json.dumps(payload)


def _workflow_factory_for(responses: list[str]):
    def factory(document_alias: str, scope: ExtractionEvaluationScope) -> ExtractionWorkflow:
        validator = ExtractionResultValidator()
        service = ExtractionService(
            extraction_repository=InMemoryExtractionRepository(),
            extraction_result_validator=validator,
        )
        return ExtractionWorkflow(
            llm_service=CannedResponseLLMService(list(responses)),
            extraction_service=service,
            extraction_result_validator=validator,
            id_generator=IdGenerator(),
            max_attempts=1,
            # Disabled for test determinism only - this environment's
            # configured default is actually enabled (it issues an extra
            # category-selection LLM call per chunk before the main
            # extraction call), which the real run (not this fake-LLM test)
            # exercises as-is.
            enable_candidate_narrowing=False,
            # Pinned for the same reason: these fixtures queue exactly one
            # canned response per expected call, assuming MULTI_FAMILY's one
            # combined call per batch. The ambient EXTRACTION_EXECUTION_STRATEGY
            # setting is a separate, mutable experiment knob and must not
            # change what this runner-level test exercises.
            execution_strategy=ExtractionExecutionStrategy.MULTI_FAMILY,
        )

    return factory


class TestRunnerEndToEnd:
    def test_matched_expectation_produces_true_positive(self) -> None:
        graph = _make_graph(
            [_make_chunk("c1", page=9, content="WARNING: Biohazard risk near pumps.")]
        )
        expectation = ExtractionExpectationCase(
            case_id="e1",
            document_alias="fake_doc",
            entity_type=ExtractionEntityType.SAFETY_WARNING,
            scope=ExtractionEvaluationScope.page_range(9, 9),
            completeness=ExtractionCompleteness.PRESENCE_ONLY,
            expected_fields={"message": "Biohazard"},
            expected_evidence=ExtractedEvidenceExpectation(page_start=9, page_end=9),
        )
        truth_set = ExtractionTruthSet(expectations=[expectation])
        response = _canned_response(
            safety_warnings=[
                {
                    "warning_type": "biological",
                    "message": "WARNING: Biohazard risk near pumps.",
                    "source_chunk_id": "c1",
                }
            ]
        )

        results = run_extraction_golden_evaluation(
            manifest=_manifest(),
            truth_set=truth_set,
            document_graphs={"fake_doc": graph},
            extraction_workflow_factory=_workflow_factory_for([response]),
        )

        assert len(results) == 1
        document_result = results[0]
        assert document_result.was_evaluated
        assert not document_result.has_execution_failures
        [scope_outcome] = document_result.scope_outcomes
        assert scope_outcome.stage_status is ExtractionStageStatus.EVALUATED
        [match] = scope_outcome.match_results
        assert match.outcome is ExtractionMatchOutcome.MATCHED
        assert match.evidence_correct is True

    def test_missing_entity_produces_false_negative(self) -> None:
        graph = _make_graph([_make_chunk("c1", page=9, content="Nothing relevant here.")])
        expectation = ExtractionExpectationCase(
            case_id="e1",
            document_alias="fake_doc",
            entity_type=ExtractionEntityType.SAFETY_WARNING,
            scope=ExtractionEvaluationScope.page_range(9, 9),
            expected_fields={"message": "Biohazard"},
        )
        truth_set = ExtractionTruthSet(expectations=[expectation])

        results = run_extraction_golden_evaluation(
            manifest=_manifest(),
            truth_set=truth_set,
            document_graphs={"fake_doc": graph},
            extraction_workflow_factory=_workflow_factory_for([_canned_response()]),
        )

        [match] = results[0].scope_outcomes[0].match_results
        assert match.outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED

    def test_page_range_scope_excludes_out_of_range_chunks(self) -> None:
        graph = _make_graph(
            [
                _make_chunk("c1", page=9, content="Relevant page."),
                _make_chunk("c2", page=200, content="Irrelevant far-away page."),
            ]
        )
        expectation = ExtractionExpectationCase(
            case_id="e1",
            document_alias="fake_doc",
            entity_type=ExtractionEntityType.SAFETY_WARNING,
            scope=ExtractionEvaluationScope.page_range(9, 9),
            expected_fields={"message": "test"},
        )
        truth_set = ExtractionTruthSet(expectations=[expectation])

        seen_chunk_counts: list[int] = []

        def factory(document_alias, scope):
            validator = ExtractionResultValidator()
            service = ExtractionService(
                extraction_repository=InMemoryExtractionRepository(),
                extraction_result_validator=validator,
            )
            workflow = ExtractionWorkflow(
                llm_service=CannedResponseLLMService([_canned_response()]),
                extraction_service=service,
                extraction_result_validator=validator,
                id_generator=IdGenerator(),
                max_attempts=1,
                enable_candidate_narrowing=False,
                # Pinned for the same reason as _workflow_factory_for above:
                # exactly one canned response is queued, assuming
                # MULTI_FAMILY's one combined call per batch.
                execution_strategy=ExtractionExecutionStrategy.MULTI_FAMILY,
            )
            original_extract = workflow.extract

            def spy_extract(*args, **kwargs):
                seen_chunk_counts.append(len(kwargs["chunks"]))
                return original_extract(*args, **kwargs)

            workflow.extract = spy_extract
            return workflow

        run_extraction_golden_evaluation(
            manifest=_manifest(),
            truth_set=truth_set,
            document_graphs={"fake_doc": graph},
            extraction_workflow_factory=factory,
        )

        assert seen_chunk_counts == [1]

    def test_applicability_declaration_alone_never_triggers_extraction(self) -> None:
        """Regression test for a real bug found during the first live Phase
        2B run: a WHOLE_DOCUMENT-scoped ExtractionApplicabilityDeclaration
        (e.g. MaintenanceInterval = NOT_APPLICABLE) with no accompanying
        ExtractionExpectationCase for that scope must NEVER cause
        `workflow.extract()` to be called - it previously did, which for
        the real 552-page MTU document meant an accidental full-document
        LLM run (183 batches) in direct violation of the explicit
        instruction never to extract the whole MTU manual."""
        graph = _make_graph(
            [
                _make_chunk("c1", page=9, content="In scope."),
                _make_chunk("c2", page=500, content="Far outside any real window."),
            ]
        )
        expectation = ExtractionExpectationCase(
            case_id="e1",
            document_alias="fake_doc",
            entity_type=ExtractionEntityType.SAFETY_WARNING,
            scope=ExtractionEvaluationScope.page_range(9, 9),
            expected_fields={"message": "test"},
        )
        declaration = ExtractionApplicabilityDeclaration(
            declaration_id="d1",
            document_alias="fake_doc",
            entity_type=ExtractionEntityType.MAINTENANCE_INTERVAL,
            scope=ExtractionEvaluationScope.whole_document(),
            applicability=ExtractionApplicability.NOT_APPLICABLE,
            reason="stated elsewhere",
        )
        truth_set = ExtractionTruthSet(
            expectations=[expectation], applicability_declarations=[declaration]
        )

        extract_call_count = 0

        def factory(document_alias, scope):
            nonlocal extract_call_count
            validator = ExtractionResultValidator()
            service = ExtractionService(
                extraction_repository=InMemoryExtractionRepository(),
                extraction_result_validator=validator,
            )
            workflow = ExtractionWorkflow(
                llm_service=CannedResponseLLMService([_canned_response()]),
                extraction_service=service,
                extraction_result_validator=validator,
                id_generator=IdGenerator(),
                max_attempts=1,
                enable_candidate_narrowing=False,
                # Pinned for the same reason as _workflow_factory_for above:
                # exactly one canned response is queued, assuming
                # MULTI_FAMILY's one combined call per batch.
                execution_strategy=ExtractionExecutionStrategy.MULTI_FAMILY,
            )
            original_extract = workflow.extract

            def spy_extract(*args, **kwargs):
                nonlocal extract_call_count
                extract_call_count += 1
                return original_extract(*args, **kwargs)

            workflow.extract = spy_extract
            return workflow

        results = run_extraction_golden_evaluation(
            manifest=_manifest(),
            truth_set=truth_set,
            document_graphs={"fake_doc": graph},
            extraction_workflow_factory=factory,
        )

        # Exactly one extraction call, for the PAGE_RANGE(9, 9) scope only -
        # never a second call for the WHOLE_DOCUMENT declaration-only scope.
        assert extract_call_count == 1

        [document_result] = results
        statuses = {
            outcome.scope.scope_type.value: outcome.stage_status
            for outcome in document_result.scope_outcomes
        }
        assert statuses["page_range"] is ExtractionStageStatus.EVALUATED
        assert statuses["whole_document"] is ExtractionStageStatus.NO_EXPECTATIONS

        whole_document_outcome = next(
            o
            for o in document_result.scope_outcomes
            if o.scope.scope_type.value == "whole_document"
        )
        assert whole_document_outcome.batch_summary is None
        assert len(whole_document_outcome.applicability_declarations) == 1

    def test_document_with_no_expectations_at_all_is_never_attempted(self) -> None:
        """Unlike Phase 1/2A's full-corpus iteration, Phase 2B only ever
        evaluates document aliases with at least one authored expectation
        or applicability declaration - an empty truth set means zero
        documents are touched (no wasted extraction calls)."""
        graph = _make_graph([_make_chunk("c1", page=1, content="x")])
        truth_set = ExtractionTruthSet(expectations=[], applicability_declarations=[])

        results = run_extraction_golden_evaluation(
            manifest=_manifest(),
            truth_set=truth_set,
            document_graphs={"fake_doc": graph},
            extraction_workflow_factory=_workflow_factory_for([]),
        )

        assert results == []
