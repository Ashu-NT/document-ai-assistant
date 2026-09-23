from collections import Counter, defaultdict

from src.application.evaluation.ingestion.effective_chunking_profile_resolver import (
    resolve_effective_chunking_profile,
)
from src.application.evaluation.ingestion.models.chunk_token_budget_result import (
    ChunkTokenBudgetEvaluationResult,
    ChunkTokenBudgetStatus,
    OversizedChunkDiagnostic,
)
from src.application.evaluation.ingestion.models.cross_reference_evaluation_result import (
    CrossReferenceEvaluationResult,
    CrossReferenceTypeMetrics,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_case import (
    ExpectedCrossReference,
    IngestionExpectationCase,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_result import (
    IngestionAssertionResult,
    IngestionExpectationCaseResult,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter_factory import (
    ChunkTokenCounterFactory,
)
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities.chunk_cross_reference import ChunkCrossReference

# The universal, always-run invariant assertion names `evaluate()` appends
# (see `_universal_invariants`) - exposed so reporting code can separate
# "chunk/structural invariant" failures from curated case-specific
# assertion failures without duplicating this set.
UNIVERSAL_INVARIANT_ASSERTION_NAMES: frozenset[str] = frozenset(
    {
        "no_empty_chunks",
        "chunk_page_provenance_present",
        "element_page_provenance_present",
        "chunk_hard_token_budget",
    }
)


class IngestionExpectationEvaluator:
    """Compares a real, freshly-built DocumentGraph (from
    ParsingWorkflow.parse() -- no DB writes, no classification/extraction)
    against one hand-labeled IngestionExpectationCase. Every populated
    `expected_*` field on the case becomes one assertion; an unset field is
    simply not checked, so a case can label only the facts someone actually
    verified rather than being forced to fill in every dimension.

    `evaluate()` also always runs a small set of universal structural/chunk
    invariants (no case-specific curation needed - these apply to any
    document): no empty chunks, a hard token-budget check against the
    EFFECTIVE chunking profile that actually produced this document's
    chunks, and page-provenance presence on every element/chunk.

    Cross-reference precision/recall/F1 by ChunkCrossReferenceType is a
    separate method, `evaluate_cross_references()`, and the token-budget
    check's full diagnostics are a separate method,
    `evaluate_chunk_token_budget()`, since both produce a metrics/diagnostic
    structure rather than a flat list of pass/fail assertions.

    `expected_document_type` is accepted on the case but not evaluated here
    -- document classification is a separate downstream stage from parsing
    and isn't run by this evaluator; leave that field unset until a
    classification-aware runner exists, or verify it manually."""

    def evaluate(
        self,
        *,
        case: IngestionExpectationCase,
        document_graph: DocumentGraph,
    ) -> IngestionExpectationCaseResult:
        assertions: list[IngestionAssertionResult] = []

        if case.expected_section_count is not None:
            assertions.append(
                self._count_assertion(
                    name="section_count",
                    expected=case.expected_section_count,
                    actual=len(document_graph.sections),
                )
            )

        if case.expected_top_level_section_titles:
            actual_titles = [
                section.title
                for section in document_graph.sections.values()
                if section.parent_section_id is None
            ]
            assertions.append(
                IngestionAssertionResult(
                    name="top_level_section_titles",
                    expected=list(case.expected_top_level_section_titles),
                    actual=actual_titles,
                    passed=actual_titles == list(case.expected_top_level_section_titles),
                )
            )

        if case.expected_chunk_count is not None:
            assertions.append(
                self._count_assertion(
                    name="chunk_count",
                    expected=case.expected_chunk_count,
                    actual=len(document_graph.chunks),
                )
            )

        if case.expected_chunk_type_counts:
            actual_counts = Counter(
                chunk.chunk_type.value for chunk in document_graph.chunks.values()
            )
            for chunk_type, expected_count in case.expected_chunk_type_counts.items():
                assertions.append(
                    self._count_assertion(
                        name=f"chunk_type_count[{chunk_type}]",
                        expected=expected_count,
                        actual=actual_counts.get(chunk_type, 0),
                    )
                )

        if case.expected_table_count is not None:
            assertions.append(
                self._count_assertion(
                    name="table_count",
                    expected=case.expected_table_count,
                    actual=len(document_graph.tables),
                )
            )

        if case.expected_picture_count is not None:
            assertions.append(
                self._count_assertion(
                    name="picture_count",
                    expected=case.expected_picture_count,
                    actual=len(document_graph.pictures),
                )
            )

        if case.expected_element_count_min is not None or case.expected_element_count_max is not None:
            assertions.append(
                self._range_assertion(
                    name="element_count_range",
                    minimum=case.expected_element_count_min,
                    maximum=case.expected_element_count_max,
                    actual=len(document_graph.elements),
                )
            )

        if case.expected_chunk_count_min is not None or case.expected_chunk_count_max is not None:
            assertions.append(
                self._range_assertion(
                    name="chunk_count_range",
                    minimum=case.expected_chunk_count_min,
                    maximum=case.expected_chunk_count_max,
                    actual=len(document_graph.chunks),
                )
            )

        if case.expected_table_count_min is not None or case.expected_table_count_max is not None:
            assertions.append(
                self._range_assertion(
                    name="table_count_range",
                    minimum=case.expected_table_count_min,
                    maximum=case.expected_table_count_max,
                    actual=len(document_graph.tables),
                )
            )

        if case.expected_picture_count_min is not None or case.expected_picture_count_max is not None:
            assertions.append(
                self._range_assertion(
                    name="picture_count_range",
                    minimum=case.expected_picture_count_min,
                    maximum=case.expected_picture_count_max,
                    actual=len(document_graph.pictures),
                )
            )

        for clue in case.required_text_clues:
            assertions.append(self._text_clue_assertion(clue, document_graph))

        for expected_cross_reference in case.expected_cross_references:
            assertions.append(
                self._cross_reference_assertion(
                    expected_cross_reference, document_graph
                )
            )

        assertions.extend(self._universal_invariants(document_graph))

        return IngestionExpectationCaseResult(
            case_id=case.case_id,
            assertions=assertions,
        )

    def evaluate_cross_references(
        self,
        *,
        case: IngestionExpectationCase,
        document_graph: DocumentGraph,
    ) -> CrossReferenceEvaluationResult:
        by_type: dict[str, list[ExpectedCrossReference]] = defaultdict(list)
        must_not_resolve: list[ExpectedCrossReference] = []
        for expected in case.expected_cross_references:
            if expected.expected_reference_type is None:
                must_not_resolve.append(expected)
            else:
                by_type[expected.expected_reference_type].append(expected)

        type_metrics: list[CrossReferenceTypeMetrics] = []
        for reference_type_value in sorted(by_type):
            expected_matches = by_type[reference_type_value]
            actual_of_type = [
                cross_reference
                for cross_reference in document_graph.cross_references.values()
                if cross_reference.reference_type.value == reference_type_value
            ]

            matched_ids: set[str] = set()
            matched_clues: list[str] = []
            missed_clues: list[str] = []
            for expected_match in expected_matches:
                candidate = self._find_matching_cross_reference(
                    expected_match,
                    candidates=[
                        cr for cr in actual_of_type
                        if cr.cross_reference_id not in matched_ids
                    ],
                )
                if candidate is not None:
                    matched_ids.add(candidate.cross_reference_id)
                    matched_clues.append(expected_match.clue)
                else:
                    missed_clues.append(expected_match.clue)

            exhaustive = reference_type_value in case.exhaustive_cross_reference_types
            false_positives = (
                len([cr for cr in actual_of_type if cr.cross_reference_id not in matched_ids])
                if exhaustive
                else None
            )

            type_metrics.append(
                CrossReferenceTypeMetrics(
                    reference_type=reference_type_value,
                    exhaustive=exhaustive,
                    true_positives=len(matched_clues),
                    false_negatives=len(missed_clues),
                    false_positives=false_positives,
                    matched_clues=tuple(matched_clues),
                    missed_clues=tuple(missed_clues),
                )
            )

        external_correct = 0
        external_incorrect = 0
        for expected in must_not_resolve:
            clue = expected.clue.lower()
            matching = [
                cr
                for cr in document_graph.cross_references.values()
                if clue in (cr.matched_text or "").lower()
            ]
            if matching:
                external_incorrect += 1
            else:
                external_correct += 1

        reconciliation_outcome_counts = Counter(
            cross_reference.reconciliation_outcome.value
            if cross_reference.reconciliation_outcome is not None
            else "(none)"
            for cross_reference in document_graph.cross_references.values()
        )

        return CrossReferenceEvaluationResult(
            case_id=case.case_id,
            type_metrics=type_metrics,
            reconciliation_outcome_counts=dict(reconciliation_outcome_counts),
            external_reference_clues_correctly_unresolved=external_correct,
            external_reference_clues_incorrectly_resolved=external_incorrect,
        )

    def evaluate_chunk_token_budget(
        self, document_graph: DocumentGraph
    ) -> ChunkTokenBudgetEvaluationResult:
        resolution = resolve_effective_chunking_profile(document_graph.document)
        if not resolution.resolved or resolution.max_chunk_tokens is None:
            return ChunkTokenBudgetEvaluationResult(
                resolved=False,
                profile=resolution.profile.value if resolution.profile else None,
                unresolved_reason=resolution.unresolved_reason,
            )

        budget = resolution.max_chunk_tokens
        counter = ChunkTokenCounterFactory().create()

        normal_count = 0
        max_observed = 0
        oversized: list[OversizedChunkDiagnostic] = []

        for chunk in document_graph.chunks.values():
            token_count = counter.count_tokens(chunk.content)
            max_observed = max(max_observed, token_count)
            if token_count <= budget:
                normal_count += 1
                continue

            # Proof, not assumption: a table-derived chunk representing
            # exactly one row is - by construction - the finest granularity
            # TableFragmentSplitter can ever produce (it only ever splits at
            # row boundaries). If that single row still exceeds budget, no
            # further splitting was possible under the current production
            # architecture. A chunk is never classified this way merely for
            # carrying a table_id - a multi-row group still over budget
            # means production's own row-accumulation guard failed to keep
            # it in bounds, which is a hard violation, not an exception.
            is_single_row_table_fragment = (
                bool(chunk.table_ids)
                and chunk.table_row_start is not None
                and chunk.table_row_end is not None
                and chunk.table_row_start == chunk.table_row_end
            )
            status = (
                ChunkTokenBudgetStatus.OVERSIZED_INDIVISIBLE
                if is_single_row_table_fragment
                else ChunkTokenBudgetStatus.HARD_BUDGET_VIOLATION
            )
            oversized.append(
                OversizedChunkDiagnostic(
                    chunk_id=chunk.chunk_id,
                    token_count=token_count,
                    budget=budget,
                    status=status,
                    chunk_type=chunk.chunk_type.value,
                    table_id=chunk.table_ids[0] if chunk.table_ids else None,
                    table_row_start=chunk.table_row_start,
                    table_row_end=chunk.table_row_end,
                )
            )

        oversized_indivisible_count = sum(
            1
            for diagnostic in oversized
            if diagnostic.status == ChunkTokenBudgetStatus.OVERSIZED_INDIVISIBLE
        )
        hard_budget_violation_count = sum(
            1
            for diagnostic in oversized
            if diagnostic.status == ChunkTokenBudgetStatus.HARD_BUDGET_VIOLATION
        )

        return ChunkTokenBudgetEvaluationResult(
            resolved=True,
            profile=resolution.profile.value if resolution.profile else None,
            effective_budget=budget,
            max_observed_tokens=max_observed,
            normal_count=normal_count,
            oversized_indivisible_count=oversized_indivisible_count,
            hard_budget_violation_count=hard_budget_violation_count,
            oversized_chunks=tuple(oversized),
        )

    @staticmethod
    def _find_matching_cross_reference(
        expected: ExpectedCrossReference,
        *,
        candidates: list[ChunkCrossReference],
    ) -> ChunkCrossReference | None:
        clue = expected.clue.lower()
        for cross_reference in candidates:
            if clue not in (cross_reference.matched_text or "").lower():
                continue
            if (
                expected.expected_target_section is not None
                and cross_reference.target_section_label != expected.expected_target_section
            ):
                continue
            if (
                expected.expected_target_annex is not None
                and cross_reference.target_annex_label != expected.expected_target_annex
            ):
                continue
            return cross_reference
        return None

    def _universal_invariants(
        self, document_graph: DocumentGraph
    ) -> list[IngestionAssertionResult]:
        return [
            self._no_empty_chunks_assertion(document_graph),
            self._chunk_provenance_assertion(document_graph),
            self._element_provenance_assertion(document_graph),
            self._chunk_token_budget_assertion(
                self.evaluate_chunk_token_budget(document_graph)
            ),
        ]

    @staticmethod
    def _no_empty_chunks_assertion(
        document_graph: DocumentGraph,
    ) -> IngestionAssertionResult:
        empty_chunk_ids = [
            chunk.chunk_id
            for chunk in document_graph.chunks.values()
            if not (chunk.content or "").strip()
        ]
        return IngestionAssertionResult(
            name="no_empty_chunks",
            expected=0,
            actual=len(empty_chunk_ids),
            passed=not empty_chunk_ids,
        )

    @staticmethod
    def _chunk_provenance_assertion(
        document_graph: DocumentGraph,
    ) -> IngestionAssertionResult:
        missing = [
            chunk.chunk_id
            for chunk in document_graph.chunks.values()
            if chunk.source is None or chunk.source.page_start is None
        ]
        return IngestionAssertionResult(
            name="chunk_page_provenance_present",
            expected=0,
            actual=len(missing),
            passed=not missing,
        )

    @staticmethod
    def _element_provenance_assertion(
        document_graph: DocumentGraph,
    ) -> IngestionAssertionResult:
        missing = [
            element.element_id
            for element in document_graph.elements.values()
            if element.source is None or element.source.page_start is None
        ]
        return IngestionAssertionResult(
            name="element_page_provenance_present",
            expected=0,
            actual=len(missing),
            passed=not missing,
        )

    @staticmethod
    def _chunk_token_budget_assertion(
        result: ChunkTokenBudgetEvaluationResult,
    ) -> IngestionAssertionResult:
        if not result.resolved:
            return IngestionAssertionResult(
                name="chunk_hard_token_budget",
                expected="effective chunking profile resolvable",
                actual=f"unresolved: {result.unresolved_reason}",
                passed=False,
            )
        return IngestionAssertionResult(
            name="chunk_hard_token_budget",
            expected=(
                f"0 hard budget violations (effective profile={result.profile!r}, "
                f"budget<={result.effective_budget} tokens)"
            ),
            actual=(
                f"{result.hard_budget_violation_count} hard violation(s), "
                f"{result.oversized_indivisible_count} oversized-indivisible "
                f"(max observed {result.max_observed_tokens} tokens)"
            ),
            passed=result.passed,
        )

    @staticmethod
    def _count_assertion(
        *, name: str, expected: int, actual: int
    ) -> IngestionAssertionResult:
        return IngestionAssertionResult(
            name=name,
            expected=expected,
            actual=actual,
            passed=actual == expected,
        )

    @staticmethod
    def _range_assertion(
        *, name: str, minimum: int | None, maximum: int | None, actual: int
    ) -> IngestionAssertionResult:
        passed = True
        if minimum is not None and actual < minimum:
            passed = False
        if maximum is not None and actual > maximum:
            passed = False
        expected_description = (
            f"[{minimum if minimum is not None else '-inf'}, "
            f"{maximum if maximum is not None else '+inf'}]"
        )
        return IngestionAssertionResult(
            name=name,
            expected=expected_description,
            actual=actual,
            passed=passed,
        )

    @staticmethod
    def _text_clue_assertion(
        clue: str, document_graph: DocumentGraph
    ) -> IngestionAssertionResult:
        clue_lower = clue.lower()
        found = any(
            clue_lower in (element.text or "").lower()
            for element in document_graph.elements.values()
        )
        return IngestionAssertionResult(
            name=f"required_text_clue[{clue}]",
            expected="present in parsed document text",
            actual="found" if found else "not found",
            passed=found,
        )

    @staticmethod
    def _cross_reference_assertion(
        expected: ExpectedCrossReference,
        document_graph: DocumentGraph,
    ) -> IngestionAssertionResult:
        clue = expected.clue.lower()
        matching = [
            cross_reference
            for cross_reference in document_graph.cross_references.values()
            if clue in (cross_reference.matched_text or "").lower()
        ]

        if expected.expected_reference_type is None:
            # A clue that must NOT produce an internal cross-reference (e.g.
            # a citation of an external standard/directive) -- passes only
            # when nothing matching was actually produced.
            return IngestionAssertionResult(
                name=f"cross_reference_absent[{expected.clue}]",
                expected="no internal cross-reference produced",
                actual=[cr.matched_text for cr in matching],
                passed=not matching,
            )

        passed = any(
            cross_reference.reference_type.value == expected.expected_reference_type
            and (
                expected.expected_target_section is None
                or cross_reference.target_section_label
                == expected.expected_target_section
            )
            and (
                expected.expected_target_annex is None
                or cross_reference.target_annex_label
                == expected.expected_target_annex
            )
            for cross_reference in matching
        )
        expected_target = expected.expected_target_section or expected.expected_target_annex
        return IngestionAssertionResult(
            name=f"cross_reference_present[{expected.clue}]",
            expected=f"{expected.expected_reference_type} -> {expected_target}",
            actual=[
                (cr.reference_type.value, cr.target_section_label, cr.target_annex_label)
                for cr in matching
            ],
            passed=passed,
        )


__all__ = ["IngestionExpectationEvaluator"]
