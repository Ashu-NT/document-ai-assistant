from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from src.application.evaluation.classification.classification_attempt_runner import (
    build_classification_attempt,
)
from src.application.evaluation.classification.classification_expectation_case import (
    ClassificationExpectationCase,
)
from src.application.evaluation.classification.golden_classification_document_result import (
    ClassificationStageStatus,
    GoldenClassificationDocumentResult,
)
from src.application.evaluation.classification.loaders.classification_expectation_loader import (
    ClassificationExpectationLoader,
)
from src.application.evaluation.corpus.evaluation_corpus_tier import (
    EvaluationCorpusTier,
)
from src.application.evaluation.corpus.golden_corpus_manifest import GoldenCorpusManifest
from src.application.evaluation.corpus.resolved_golden_document import (
    GoldenDocumentAvailability,
)
from src.application.evaluation.golden.cache_only_parser_guard import (
    CacheOnlyParserGuard,
)
from src.application.evaluation.golden.corpus_coverage_summary import (
    CorpusCoverageSummary,
)
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationOutcome,
    GoldenDocumentEvaluationStatus,
)
from src.application.evaluation.golden.golden_document_parse_stage import (
    parse_golden_document,
)
from src.application.evaluation.reproducibility import build_evaluation_run_metadata
from src.application.orchestrator.ingestion.parsing_runtime_builder import (
    build_parsing_runtime,
)
from src.application.prompts.classification import DOCUMENT_CLASSIFICATION_PROMPT_VERSION
from src.application.services.ai import LLMService
from src.application.validation.classification import DocumentClassificationValidator
from src.application.workflows.classification import DocumentClassificationWorkflow
from src.config.settings import classification_settings, llm_settings
from src.infrastructure.ai.llm import OllamaLLMProvider
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator

if TYPE_CHECKING:
    # Deferred to avoid a module-load-time circular import:
    # golden_evaluation_report.py itself imports the classification
    # package (for GoldenEvaluationReport.classification_metrics), so this
    # module can only reach GoldenEvaluationReport at call time, not import
    # time. `from __future__ import annotations` keeps the return-type
    # annotation below lazy so this TYPE_CHECKING-only import is enough for
    # type checkers without re-introducing the cycle at runtime.
    from src.application.evaluation.golden.golden_evaluation_report import (
        GoldenEvaluationReport,
    )

FRESH_MODEL_EXECUTION_MODE = "fresh_model"


def run_classification_golden_evaluation(
    *,
    manifest: GoldenCorpusManifest | None = None,
    expectation_cases_path: Path | str | None = None,
    allow_real_parsing: bool = True,
    parsing_workflow=None,
    classification_workflow: DocumentClassificationWorkflow | None = None,
    confidence_threshold: float | None = None,
    tiers: frozenset[EvaluationCorpusTier] | None = None,
) -> GoldenEvaluationReport:
    """Evaluates classification (only) for every document in the golden
    corpus manifest through the real production classification path
    (Parsed Artifact Store -> ParsingWorkflow -> DocumentGraph -> fresh
    production classification -> ClassificationAttempt -> golden metrics),
    never running structural/chunking/cross-reference evaluation (that
    remains `run_fast_golden_regression`'s job) and never running
    extraction/embeddings/retrieval (Phase 2B/later).

    Always FRESH_MODEL: every document is classified via
    `DocumentClassificationWorkflow.classify_document_attempt()`, which
    structurally never consults `allow_reclassification`/`use_cache` at
    all - not merely called with those flags overridden. This is recorded
    in `EvaluationRunMetadata.classification_execution_mode` for
    reproducibility.

    `parsing_workflow`/`classification_workflow` are injectable (tests use
    fakes); the production default builds the real runtimes.
    """
    resolved_manifest = manifest or GoldenCorpusManifest.default()
    resolved_documents = resolved_manifest.resolve_all(tiers=tiers)

    expectations_by_alias = _load_expectations_by_alias(
        expectation_cases_path, manifest=resolved_manifest
    )

    id_generator = IdGenerator()
    if parsing_workflow is None:
        parsing_workflow, _ = build_parsing_runtime(id_generator=id_generator)
    if not allow_real_parsing:
        parsing_workflow.parser = CacheOnlyParserGuard(parsing_workflow.parser)

    resolved_workflow = classification_workflow or _build_default_classification_workflow(
        id_generator=id_generator
    )
    resolved_threshold = (
        confidence_threshold
        if confidence_threshold is not None
        else classification_settings.confidence_threshold
    )
    validator = DocumentClassificationValidator()

    document_outcomes: list[GoldenDocumentEvaluationOutcome] = []
    classification_results: list[GoldenClassificationDocumentResult] = []

    for resolved in resolved_documents:
        parse_outcome = parse_golden_document(
            resolved=resolved,
            parsing_workflow=parsing_workflow,
            id_generator=id_generator,
        )
        document_outcomes.append(
            GoldenDocumentEvaluationOutcome(
                alias=parse_outcome.alias,
                status=parse_outcome.status,
                detail=parse_outcome.detail,
            )
        )

        expectation = expectations_by_alias.get(resolved.alias)
        if parse_outcome.status != GoldenDocumentEvaluationStatus.EVALUATED:
            classification_results.append(
                GoldenClassificationDocumentResult(
                    alias=resolved.alias,
                    stage_status=ClassificationStageStatus.SKIPPED_PARSING_UNAVAILABLE,
                    expectation=expectation,
                    detail=(
                        f"parsing stage status was {parse_outcome.status.value}: "
                        f"{parse_outcome.detail}"
                    ),
                )
            )
            continue

        attempt_outcome = build_classification_attempt(
            resolved_workflow,
            parse_outcome.document_graph,
            document_alias=resolved.alias,
            confidence_threshold=resolved_threshold,
            validator=validator,
        )
        if not attempt_outcome.succeeded:
            classification_results.append(
                GoldenClassificationDocumentResult(
                    alias=resolved.alias,
                    stage_status=ClassificationStageStatus.EXECUTION_FAILED,
                    expectation=expectation,
                    execution_error=attempt_outcome.execution_error,
                )
            )
            continue

        classification_results.append(
            GoldenClassificationDocumentResult(
                alias=resolved.alias,
                stage_status=ClassificationStageStatus.EVALUATED,
                expectation=expectation,
                attempt=attempt_outcome.attempt,
            )
        )

    coverage = CorpusCoverageSummary(
        expected=len(resolved_documents),
        available=sum(1 for r in resolved_documents if r.is_available),
        evaluated=sum(1 for o in document_outcomes if o.was_evaluated),
        missing_aliases=tuple(
            r.alias
            for r in resolved_documents
            if r.availability == GoldenDocumentAvailability.MISSING
        ),
        hash_mismatch_aliases=tuple(
            r.alias
            for r in resolved_documents
            if r.availability == GoldenDocumentAvailability.HASH_MISMATCH
        ),
    )

    run_metadata = build_evaluation_run_metadata(
        parser_name=getattr(parsing_workflow.parser, "parser_name", None),
        parser_version=getattr(parsing_workflow.parser, "parser_version", None),
        conversion_fingerprint=_resolve_conversion_fingerprint(parsing_workflow.parser),
        evaluation_config={"allow_real_parsing": allow_real_parsing},
        classification_model=resolved_workflow.classification_model,
        classification_execution_mode=FRESH_MODEL_EXECUTION_MODE,
        classification_confidence_threshold=resolved_threshold,
        classification_allow_reclassification=classification_settings.allow_reclassification,
        classification_use_cache=classification_settings.use_cache,
        classification_prompt_version=DOCUMENT_CLASSIFICATION_PROMPT_VERSION,
    )

    from src.application.evaluation.golden.golden_evaluation_report import (
        GoldenEvaluationReport,
    )

    return GoldenEvaluationReport(
        run_metadata=run_metadata,
        corpus_coverage=coverage,
        document_outcomes=document_outcomes,
        classification_results=classification_results,
    )


def _load_expectations_by_alias(
    expectation_cases_path: Path | str | None,
    *,
    manifest: GoldenCorpusManifest,
) -> dict[str, ClassificationExpectationCase]:
    try:
        cases = ClassificationExpectationLoader(manifest=manifest).load(
            expectation_cases_path
        )
    except SchemaValidationError:
        if expectation_cases_path is not None:
            raise
        # No classification-expectation fixtures exist yet in this
        # environment - every document is still classified, just with no
        # golden label to score against (see NO reviewed/candidate label ->
        # excluded from accuracy denominators, never fabricated).
        cases = []

    return {case.document_alias: case for case in cases}


def _build_default_classification_workflow(
    *, id_generator: IdGenerator
) -> DocumentClassificationWorkflow:
    llm_service = LLMService(
        OllamaLLMProvider(
            base_url=llm_settings.ollama_base_url,
            default_model=llm_settings.general_llm,
        )
    )
    return DocumentClassificationWorkflow(
        llm_service=llm_service,
        classification_service=None,  # type: ignore[arg-type]
        document_classification_validator=DocumentClassificationValidator(),
        id_generator=id_generator,
    )


def _resolve_conversion_fingerprint(parser) -> str | None:
    fingerprint_resolver = getattr(parser, "resolve_conversion_fingerprint", None)
    if fingerprint_resolver is None:
        return None
    try:
        return fingerprint_resolver()
    except Exception:  # noqa: BLE001 - reproducibility metadata is a
        # best-effort nicety; a fingerprint failure must never abort
        # evaluation itself.
        return None


__all__ = ["FRESH_MODEL_EXECUTION_MODE", "run_classification_golden_evaluation"]
