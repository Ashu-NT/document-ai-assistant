from pathlib import Path

from src.application.evaluation.corpus.golden_corpus_manifest import GoldenCorpusManifest
from src.application.evaluation.corpus.resolved_golden_document import (
    GoldenDocumentAvailability,
)
from src.application.evaluation.golden.cache_only_parser_guard import (
    CacheOnlyParserGuard,
    GoldenCorpusDoclingUnavailableError,
)
from src.application.evaluation.golden.corpus_coverage_summary import (
    CorpusCoverageSummary,
)
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationOutcome,
    GoldenDocumentEvaluationStatus,
)
from src.application.evaluation.golden.golden_evaluation_report import (
    GoldenEvaluationReport,
)
from src.application.evaluation.ingestion.ingestion_expectation_evaluator import (
    IngestionExpectationEvaluator,
)
from src.application.evaluation.ingestion.loaders.ingestion_truth_set_loader import (
    IngestionTruthSetLoader,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_case import (
    IngestionExpectationCase,
)
from src.application.evaluation.reproducibility import build_evaluation_run_metadata
from src.application.orchestrator.ingestion.parsing_runtime_builder import (
    build_parsing_runtime,
)
from src.shared.exceptions import ApplicationError, SchemaValidationError
from src.shared.ids import IdGenerator, IdPrefix


def run_fast_golden_regression(
    *,
    manifest: GoldenCorpusManifest | None = None,
    structural_cases_path: Path | str | None = None,
    allow_real_parsing: bool = True,
    parsing_workflow=None,
    evaluator: IngestionExpectationEvaluator | None = None,
) -> GoldenEvaluationReport:
    """Evaluates every document in the golden corpus manifest through the
    real production parsing path (Parsed Artifact Store -> ParsingWorkflow
    -> structural expectations -> section/chunk invariants -> cross-
    reference expectations), never running classification, extraction,
    embeddings, or retrieval.

    `allow_real_parsing=False` runs in cached-only mode: a document with no
    already-cached parsed artifact is recorded as
    CACHE_MISS_IN_CACHED_ONLY_MODE rather than triggering a real (possibly
    slow, possibly Docling-dependent) conversion. Every manifest entry gets
    an explicit outcome regardless of corpus/cache availability - see
    GoldenDocumentEvaluationStatus - so a partial corpus can never be
    reported as a fully evaluated one.

    `parsing_workflow`/`evaluator` are injectable (tests use a fake
    parsing_workflow so they never need real Docling/a real corpus); the
    production default builds the real runtime via `build_parsing_runtime`.
    """
    resolved_manifest = manifest or GoldenCorpusManifest.default()
    resolved_documents = resolved_manifest.resolve_all()

    cases_by_alias = _load_structural_cases_by_alias(structural_cases_path)

    id_generator = IdGenerator()
    if parsing_workflow is None:
        parsing_workflow, _ = build_parsing_runtime(id_generator=id_generator)
    if not allow_real_parsing:
        parsing_workflow.parser = CacheOnlyParserGuard(parsing_workflow.parser)

    evaluator = evaluator or IngestionExpectationEvaluator()
    document_outcomes: list[GoldenDocumentEvaluationOutcome] = []

    for resolved in resolved_documents:
        outcome = _evaluate_one_document(
            resolved=resolved,
            case=cases_by_alias.get(resolved.alias),
            parsing_workflow=parsing_workflow,
            evaluator=evaluator,
            id_generator=id_generator,
        )
        document_outcomes.append(outcome)

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
    )

    return GoldenEvaluationReport(
        run_metadata=run_metadata,
        corpus_coverage=coverage,
        document_outcomes=document_outcomes,
    )


def _evaluate_one_document(
    *,
    resolved,
    case: IngestionExpectationCase | None,
    parsing_workflow,
    evaluator: IngestionExpectationEvaluator,
    id_generator: IdGenerator,
) -> GoldenDocumentEvaluationOutcome:
    if resolved.availability == GoldenDocumentAvailability.MISSING:
        return GoldenDocumentEvaluationOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.CORPUS_MISSING,
            detail=f"expected file not found at {resolved.absolute_path}",
        )

    if resolved.availability == GoldenDocumentAvailability.HASH_MISMATCH:
        return GoldenDocumentEvaluationOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.CORPUS_HASH_MISMATCH,
            detail=(
                f"expected sha256={resolved.entry.expected_sha256} "
                f"actual={resolved.actual_sha256}"
            ),
        )

    resolved_case = case or IngestionExpectationCase(
        case_id=f"struct_{resolved.alias}_default",
        document_path=resolved.absolute_path,
        document_alias=resolved.alias,
    )

    document_id = id_generator.new_id(IdPrefix.DOCUMENT)
    try:
        parse_result = parsing_workflow.parse(
            file_path=str(resolved.absolute_path),
            file_hash=resolved.actual_sha256,
            content_hash=None,
            document_id=document_id,
        )
    except GoldenCorpusDoclingUnavailableError as exc:
        return GoldenDocumentEvaluationOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.CACHE_MISS_IN_CACHED_ONLY_MODE,
            detail=str(exc),
        )
    except ApplicationError as exc:
        # Fault isolation across an independent unit of work in a
        # multi-document batch: one document's real Docling failure must
        # not silently abort evaluation of the other nine, but must also
        # never disappear - it is recorded as an explicit, visible outcome.
        return GoldenDocumentEvaluationOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.PARSE_FAILED,
            detail=repr(exc),
        )

    structural_result = evaluator.evaluate(
        case=resolved_case, document_graph=parse_result.document_graph
    )
    cross_reference_result = evaluator.evaluate_cross_references(
        case=resolved_case, document_graph=parse_result.document_graph
    )
    chunk_token_budget_result = evaluator.evaluate_chunk_token_budget(
        parse_result.document_graph
    )
    return GoldenDocumentEvaluationOutcome(
        alias=resolved.alias,
        status=GoldenDocumentEvaluationStatus.EVALUATED,
        structural_result=structural_result,
        cross_reference_result=cross_reference_result,
        chunk_token_budget_result=chunk_token_budget_result,
    )


def _load_structural_cases_by_alias(
    structural_cases_path: Path | str | None,
) -> dict[str, IngestionExpectationCase]:
    try:
        cases = IngestionTruthSetLoader().load(structural_cases_path)
    except SchemaValidationError:
        if structural_cases_path is not None:
            raise
        # No structural-expectation fixtures exist yet in this environment -
        # every document still gets evaluated, just with no curated
        # case-specific assertions (universal invariants still run).
        cases = []

    return {case.document_alias: case for case in cases if case.document_alias}


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


__all__ = ["run_fast_golden_regression"]
