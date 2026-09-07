from collections import Counter

from src.application.evaluation.ingestion.models.ingestion_expectation_case import (
    ExpectedCrossReference,
    IngestionExpectationCase,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_result import (
    IngestionAssertionResult,
    IngestionExpectationCaseResult,
)
from src.domain.document.aggregates.document_graph import DocumentGraph


class IngestionExpectationEvaluator:
    """Compares a real, freshly-built DocumentGraph (from
    ParsingWorkflow.parse() -- no DB writes, no classification/extraction)
    against one hand-labeled IngestionExpectationCase. Every populated
    `expected_*` field on the case becomes one assertion; an unset field is
    simply not checked, so a case can label only the facts someone actually
    verified rather than being forced to fill in every dimension.

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

        for expected_cross_reference in case.expected_cross_references:
            assertions.append(
                self._cross_reference_assertion(
                    expected_cross_reference, document_graph
                )
            )

        return IngestionExpectationCaseResult(
            case_id=case.case_id,
            assertions=assertions,
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
            for cross_reference in matching
        )
        return IngestionAssertionResult(
            name=f"cross_reference_present[{expected.clue}]",
            expected=(
                f"{expected.expected_reference_type} -> "
                f"{expected.expected_target_section}"
            ),
            actual=[
                (cr.reference_type.value, cr.target_section_label)
                for cr in matching
            ],
            passed=passed,
        )


__all__ = ["IngestionExpectationEvaluator"]
