"""Phase 2B golden extraction evaluation runner.

Drives the REAL production `ExtractionWorkflow.extract()` - never a second
extractor. Isolation is achieved purely through the two seams the Phase 2B
research trace confirmed are already swappable without any production code
change: the LLM port (`llm_service`) and the persistence port
(`extraction_service` backed by `InMemoryExtractionRepository`). PAGE_RANGE
scoping is achieved by filtering the real `DocumentGraph`'s chunks by page
overlap before calling `extract()` - also already supported (see
`ExtractionRetryStep`'s partial-chunk-list precedent), no production change
needed.
"""

import re
from collections.abc import Callable
from dataclasses import replace as dataclass_replace

from src.application.evaluation.corpus.golden_corpus_manifest import (
    GoldenCorpusManifest,
)
from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
    ExtractionScopeType,
)
from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.evaluation.extraction.extraction_evidence_matcher import (
    evaluate_evidence,
    resolve_evidence_input,
)
from src.application.evaluation.extraction.extraction_field_extraction import (
    extract_actual_fields,
)
from src.application.evaluation.extraction.extraction_isolation import (
    InMemoryExtractionRepository,
)
from src.application.evaluation.extraction.golden_extraction_document_result import (
    ExtractionBatchSummary,
    ExtractionScopeRunOutcome,
    ExtractionStageStatus,
    GoldenExtractionDocumentResult,
)
from src.application.evaluation.extraction.loaders.extraction_expectation_loader import (
    ExtractionExpectationLoader,
    ExtractionTruthSet,
)
from src.application.evaluation.extraction.matchers.extraction_entity_matcher import (
    _ActualEntity,
    match_expectations_against_actuals,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
)
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationStatus,
)
from src.application.evaluation.golden.golden_document_parse_stage import (
    parse_golden_document,
)
from src.domain.document import DocumentChunk, DocumentGraph
from src.domain.extraction import ExtractionResult
from src.shared.ids import IdGenerator

_RESULT_ATTRIBUTE_NAMES: dict[ExtractionEntityType, str] = {
    ExtractionEntityType.MAINTENANCE_TASK: "maintenance_tasks",
    ExtractionEntityType.SPARE_PART: "spare_parts",
    ExtractionEntityType.EQUIPMENT_INFO: "equipment",
    ExtractionEntityType.MANUFACTURER: "manufacturers",
    ExtractionEntityType.SUPPLIER: "suppliers",
    ExtractionEntityType.CONTACT_POINT: "contact_points",
    ExtractionEntityType.PROCEDURE: "procedures",
    ExtractionEntityType.SPECIFICATION: "specifications",
    ExtractionEntityType.SAFETY_WARNING: "safety_warnings",
    ExtractionEntityType.MAINTENANCE_INTERVAL: "maintenance_intervals",
    ExtractionEntityType.TROUBLESHOOTING_ENTRY: "troubleshooting_entries",
    ExtractionEntityType.EXTRACTED_IDENTIFIER: "extracted_identifiers",
}

_ENTITY_ID_FIELD_NAMES: dict[ExtractionEntityType, str] = {
    ExtractionEntityType.MAINTENANCE_TASK: "task_id",
    ExtractionEntityType.SPARE_PART: "spare_part_id",
    ExtractionEntityType.EQUIPMENT_INFO: "equipment_id",
    ExtractionEntityType.MANUFACTURER: "manufacturer_id",
    ExtractionEntityType.SUPPLIER: "supplier_id",
    ExtractionEntityType.CONTACT_POINT: "contact_point_id",
    ExtractionEntityType.PROCEDURE: "procedure_id",
    ExtractionEntityType.SPECIFICATION: "specification_id",
    ExtractionEntityType.SAFETY_WARNING: "safety_warning_id",
    ExtractionEntityType.MAINTENANCE_INTERVAL: "maintenance_interval_id",
    ExtractionEntityType.TROUBLESHOOTING_ENTRY: "troubleshooting_id",
    # ExtractedIdentifier has no own id field (confirmed in the research
    # trace) - a synthetic index-based id is used instead, see `_entity_id`.
}

_DROPPED_EMPTY_PATTERN = re.compile(r"Dropped (\d+) extracted item")


def _entity_id(entity_type: ExtractionEntityType, entity: object, index: int) -> str:
    field_name = _ENTITY_ID_FIELD_NAMES.get(entity_type)
    value = getattr(entity, field_name, None) if field_name else None
    return value or f"{entity_type.value}::{index}"


def _chunk_page_bounds(chunk: DocumentChunk) -> tuple[int | None, int | None]:
    if chunk.source is None:
        return (None, None)
    return (chunk.source.page_start, chunk.source.page_end)


def _select_scope_chunks(
    scope: ExtractionEvaluationScope, chunks: list[DocumentChunk]
) -> list[DocumentChunk]:
    if scope.scope_type is ExtractionScopeType.WHOLE_DOCUMENT:
        return list(chunks)
    return [
        chunk
        for chunk in chunks
        if scope.overlaps_pages(*_chunk_page_bounds(chunk))
    ]


def _build_batch_summary(
    workflow: object, progress_messages: list[str]
) -> ExtractionBatchSummary:
    diagnostics = list(getattr(workflow, "last_batch_diagnostics", []) or [])
    parse_success_count = sum(
        1 for diagnostic in diagnostics if getattr(diagnostic, "parse_success", False)
    )
    parse_failure_count = len(diagnostics) - parse_success_count

    dropped_empty_count = 0
    invalid_source_chunk_id_event_count = 0
    for message in progress_messages:
        match = _DROPPED_EMPTY_PATTERN.search(message)
        if match:
            dropped_empty_count += int(match.group(1))
        lowered = message.lower()
        if "invalid" in lowered and "chunk" in lowered and "source" in lowered:
            invalid_source_chunk_id_event_count += 1

    return ExtractionBatchSummary(
        batch_count=len(diagnostics),
        parse_success_count=parse_success_count,
        parse_failure_count=parse_failure_count,
        dropped_empty_count=dropped_empty_count,
        invalid_source_chunk_id_event_count=invalid_source_chunk_id_event_count,
    )


def _default_extraction_workflow_factory(
    document_alias: str, scope: ExtractionEvaluationScope
):
    from src.application.services.ai import LLMService
    from src.application.services.extraction import ExtractionService
    from src.application.validation.extraction import ExtractionResultValidator
    from src.application.workflows.extraction import ExtractionWorkflow
    from src.config.settings import llm_settings
    from src.infrastructure.ai.llm import OllamaLLMProvider

    llm_service = LLMService(
        OllamaLLMProvider(
            base_url=llm_settings.ollama_base_url,
            default_model=llm_settings.extraction_llm or llm_settings.general_llm,
        )
    )
    validator = ExtractionResultValidator()
    service = ExtractionService(
        extraction_repository=InMemoryExtractionRepository(),
        extraction_result_validator=validator,
    )
    return ExtractionWorkflow(
        llm_service=llm_service,
        extraction_service=service,
        extraction_result_validator=validator,
        id_generator=IdGenerator(),
    )


def _evaluate_scope(
    *,
    alias: str,
    scope: ExtractionEvaluationScope,
    graph: DocumentGraph,
    doc_expectations: list,
    doc_declarations: list,
    extraction_workflow_factory: Callable,
) -> ExtractionScopeRunOutcome:
    chunks = _select_scope_chunks(scope, list(graph.chunks.values()))
    if not chunks:
        return ExtractionScopeRunOutcome(
            document_alias=alias,
            scope=scope,
            stage_status=ExtractionStageStatus.EXECUTION_FAILED,
            execution_error=(
                f"no chunks overlap the requested scope ({scope.scope_type.value} "
                f"{scope.page_start}-{scope.page_end}) - cannot run extraction"
            ),
            applicability_declarations=doc_declarations,
        )

    workflow = extraction_workflow_factory(alias, scope)
    progress_messages: list[str] = []

    try:
        extraction_result: ExtractionResult = workflow.extract(
            document_id=graph.document.document_id,
            chunks=chunks,
            tables=graph.tables,
            sections=graph.sections,
            progress_callback=progress_messages.append,
        )
    except Exception as exc:  # noqa: BLE001 - any real production failure mode
        # (SchemaValidationError, LLMProviderError, extraction-result
        # validation failure, ...) must surface as an explicit, visible
        # per-scope outcome, never silently abort the whole evaluation run.
        return ExtractionScopeRunOutcome(
            document_alias=alias,
            scope=scope,
            stage_status=ExtractionStageStatus.EXECUTION_FAILED,
            execution_error=repr(exc),
            applicability_declarations=doc_declarations,
        )

    batch_summary = _build_batch_summary(workflow, progress_messages)
    chunk_page_lookup = {
        chunk.chunk_id: _chunk_page_bounds(chunk) for chunk in chunks
    }

    match_results = []
    entity_types_needed = {expectation.entity_type for expectation in doc_expectations}
    for entity_type in entity_types_needed:
        type_expectations = [
            expectation
            for expectation in doc_expectations
            if expectation.entity_type is entity_type
        ]
        actual_list = list(
            getattr(extraction_result, _RESULT_ATTRIBUTE_NAMES[entity_type])
        )
        actual_entities = [
            _ActualEntity(
                entity_id=_entity_id(entity_type, entity, index),
                fields=extract_actual_fields(entity, entity_type),
            )
            for index, entity in enumerate(actual_list)
        ]
        entity_by_id = {
            actual.entity_id: entity
            for actual, entity in zip(actual_entities, actual_list, strict=True)
        }

        type_match_results = match_expectations_against_actuals(
            entity_type.value, type_expectations, actual_entities
        )
        for match in type_match_results:
            if (
                match.outcome is ExtractionMatchOutcome.MATCHED
                and match.actual_entity_id is not None
            ):
                entity = entity_by_id[match.actual_entity_id]
                evidence_input = resolve_evidence_input(
                    entity, chunk_page_lookup=chunk_page_lookup
                )
                expected_evidence = (
                    match.expectation.expected_evidence
                    if match.expectation is not None
                    else None
                )
                evidence_result = evaluate_evidence(expected_evidence, evidence_input)
                match = dataclass_replace(
                    match,
                    evidence_correct=evidence_result.evidence_correct,
                    evidence_detail=evidence_result.detail,
                )
            match_results.append(match)

    return ExtractionScopeRunOutcome(
        document_alias=alias,
        scope=scope,
        stage_status=ExtractionStageStatus.EVALUATED,
        batch_summary=batch_summary,
        match_results=match_results,
        applicability_declarations=doc_declarations,
    )


def _evaluate_document(
    *,
    alias: str,
    truth_set: ExtractionTruthSet,
    manifest: GoldenCorpusManifest,
    parsing_workflow: object,
    document_graphs: dict[str, DocumentGraph],
    extraction_workflow_factory: Callable,
    id_generator: IdGenerator,
) -> GoldenExtractionDocumentResult:
    doc_expectations = [
        expectation
        for expectation in truth_set.expectations
        if expectation.document_alias == alias
    ]
    doc_declarations = [
        declaration
        for declaration in truth_set.applicability_declarations
        if declaration.document_alias == alias
    ]

    graph = document_graphs.get(alias)
    if graph is None:
        resolved = manifest.resolve(alias)
        parse_outcome = parse_golden_document(
            resolved=resolved,
            parsing_workflow=parsing_workflow,
            id_generator=id_generator,
        )
        if (
            parse_outcome.status is not GoldenDocumentEvaluationStatus.EVALUATED
            or parse_outcome.document_graph is None
        ):
            return GoldenExtractionDocumentResult(
                alias=alias,
                scope_outcomes=[
                    ExtractionScopeRunOutcome(
                        document_alias=alias,
                        scope=ExtractionEvaluationScope.whole_document(),
                        stage_status=ExtractionStageStatus.SKIPPED_PARSING_UNAVAILABLE,
                        execution_error=parse_outcome.detail,
                        applicability_declarations=doc_declarations,
                    )
                ],
            )
        graph = parse_outcome.document_graph

    def _sort_key(scope: ExtractionEvaluationScope):
        return (scope.scope_type.value, scope.page_start or 0, scope.page_end or 0)

    # Only scopes with at least one real ExtractionExpectationCase ever
    # trigger `workflow.extract()`. An ExtractionApplicabilityDeclaration is
    # a static judgment, never a reason to run extraction by itself - a
    # WHOLE_DOCUMENT-scoped declaration (e.g. MaintenanceInterval =
    # NOT_APPLICABLE) must NEVER cause a whole-document extraction call
    # (see task instruction: never run the LLM over the entire MTU manual).
    extraction_scopes = sorted(
        {expectation.scope for expectation in doc_expectations}, key=_sort_key
    )
    declaration_only_scopes = sorted(
        {
            declaration.scope
            for declaration in doc_declarations
            if declaration.scope not in extraction_scopes
        },
        key=_sort_key,
    )

    if not extraction_scopes and not declaration_only_scopes:
        return GoldenExtractionDocumentResult(
            alias=alias,
            scope_outcomes=[
                ExtractionScopeRunOutcome(
                    document_alias=alias,
                    scope=ExtractionEvaluationScope.whole_document(),
                    stage_status=ExtractionStageStatus.NO_EXPECTATIONS,
                )
            ],
        )

    scope_outcomes = [
        _evaluate_scope(
            alias=alias,
            scope=scope,
            graph=graph,
            doc_expectations=[e for e in doc_expectations if e.scope == scope],
            doc_declarations=[d for d in doc_declarations if d.scope == scope],
            extraction_workflow_factory=extraction_workflow_factory,
        )
        for scope in extraction_scopes
    ]
    scope_outcomes += [
        ExtractionScopeRunOutcome(
            document_alias=alias,
            scope=scope,
            stage_status=ExtractionStageStatus.NO_EXPECTATIONS,
            applicability_declarations=[
                d for d in doc_declarations if d.scope == scope
            ],
        )
        for scope in declaration_only_scopes
    ]

    return GoldenExtractionDocumentResult(alias=alias, scope_outcomes=scope_outcomes)


def run_extraction_golden_evaluation(
    *,
    manifest: GoldenCorpusManifest | None = None,
    truth_set: ExtractionTruthSet | None = None,
    parsing_workflow: object | None = None,
    document_graphs: dict[str, DocumentGraph] | None = None,
    extraction_workflow_factory: Callable | None = None,
    id_generator: IdGenerator | None = None,
) -> list[GoldenExtractionDocumentResult]:
    """Evaluates every document alias that has at least one Phase 2B
    expectation or applicability declaration authored for it - deliberately
    NOT every document in the corpus (Phase 2B's initial truth set is a
    small, selective subset, unlike Phase 1/2A's full-corpus iteration).

    `document_graphs` lets a caller pre-supply an already-built
    `DocumentGraph` for an alias (e.g. the MTU CHALLENGE document, built via
    the supplied-artifact substitution pattern - see
    test_mtu_challenge_structural_regression.py) instead of going through
    `parse_golden_document`, which only knows how to run a live/cached
    Docling parse.
    """
    resolved_manifest = manifest or GoldenCorpusManifest.default()
    resolved_truth_set = truth_set or ExtractionExpectationLoader(
        manifest=resolved_manifest
    ).load()
    resolved_id_generator = id_generator or IdGenerator()
    resolved_document_graphs = document_graphs or {}
    resolved_factory = extraction_workflow_factory or _default_extraction_workflow_factory

    resolved_parsing_workflow = parsing_workflow
    if resolved_parsing_workflow is None:
        needs_real_parsing = any(
            alias not in resolved_document_graphs
            for alias in {
                expectation.document_alias
                for expectation in resolved_truth_set.expectations
            }
            | {
                declaration.document_alias
                for declaration in resolved_truth_set.applicability_declarations
            }
        )
        if needs_real_parsing:
            from src.application.orchestrator.ingestion.parsing_runtime_builder import (
                build_parsing_runtime,
            )

            resolved_parsing_workflow, _ = build_parsing_runtime(
                id_generator=resolved_id_generator
            )

    aliases = sorted(
        {expectation.document_alias for expectation in resolved_truth_set.expectations}
        | {
            declaration.document_alias
            for declaration in resolved_truth_set.applicability_declarations
        }
    )

    return [
        _evaluate_document(
            alias=alias,
            truth_set=resolved_truth_set,
            manifest=resolved_manifest,
            parsing_workflow=resolved_parsing_workflow,
            document_graphs=resolved_document_graphs,
            extraction_workflow_factory=resolved_factory,
            id_generator=resolved_id_generator,
        )
        for alias in aliases
    ]


__all__ = ["run_extraction_golden_evaluation"]
