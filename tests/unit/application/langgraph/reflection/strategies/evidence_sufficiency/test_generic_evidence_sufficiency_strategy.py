from src.application.langgraph.reflection.decomposition import (
    ClauseCoverage,
    MultiClauseCoverageResult,
)
from src.application.langgraph.reflection.models import (
    AnswerQuality,
    EvidenceQuality,
    SufficiencyVerdictType,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency import (
    EvidenceSufficiencyContext,
    GenericEvidenceSufficiencyStrategy,
)


def _answer_quality(**overrides) -> AnswerQuality:
    defaults = dict(
        answered_question=True,
        contains_requested_information=True,
        contains_page_reference=True,
        contains_grounding=True,
        complete_enough=True,
        concise_enough=True,
        referenced_pages=[1],
        unexpected_pages=[],
        missing_pages=[],
        page_coverage_ratio=1.0,
        has_duplicate_content=False,
        duplicate_line_count=0,
        score=1.0,
    )
    defaults.update(overrides)
    return AnswerQuality(**defaults)


def _evidence_quality(**overrides) -> EvidenceQuality:
    defaults = dict(
        approved_chunk_count=1,
        rejected_chunk_count=0,
        document_ids=["doc_1"],
        page_numbers=[1],
        missing_pages=[],
        page_coverage_ratio=1.0,
        has_document_leakage=False,
        has_sufficient_evidence=True,
        score=1.0,
    )
    defaults.update(overrides)
    return EvidenceQuality(**defaults)


def _context(**overrides) -> EvidenceSufficiencyContext:
    defaults = dict(
        question="What is the operating pressure?",
        answer_text="The operating pressure is 6 bar.",
        answer_intent="specification_summary",
        selected_document_id="doc_1",
        approved_chunks=[{"document_id": "doc_1", "content": "operating pressure 6 bar"}],
        rejected_chunks=[],
        evidence_quality=_evidence_quality(),
        answer_quality=_answer_quality(),
    )
    defaults.update(overrides)
    return EvidenceSufficiencyContext(**defaults)


def test_generic_strategy_is_sufficient_when_all_generic_signals_are_good() -> None:
    strategy = GenericEvidenceSufficiencyStrategy()

    verdict = strategy.is_answer_sufficient(_context())

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT
    assert verdict.is_sufficient is True


def test_generic_strategy_is_insufficient_when_evidence_is_not_sufficient() -> None:
    strategy = GenericEvidenceSufficiencyStrategy()

    verdict = strategy.is_answer_sufficient(
        _context(evidence_quality=_evidence_quality(has_sufficient_evidence=False))
    )

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY
    assert "supporting evidence for the question" in verdict.missing_information


def test_generic_strategy_is_insufficient_when_answer_does_not_contain_requested_information() -> None:
    strategy = GenericEvidenceSufficiencyStrategy()

    verdict = strategy.is_answer_sufficient(
        _context(answer_quality=_answer_quality(contains_requested_information=False))
    )

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY
    assert "information that directly answers the question" in verdict.missing_information


def test_generic_strategy_is_insufficient_when_answer_has_duplicate_content() -> None:
    strategy = GenericEvidenceSufficiencyStrategy()

    verdict = strategy.is_answer_sufficient(
        _context(answer_quality=_answer_quality(has_duplicate_content=True))
    )

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY


def test_generic_strategy_is_insufficient_when_answer_cites_unexpected_pages() -> None:
    strategy = GenericEvidenceSufficiencyStrategy()

    verdict = strategy.is_answer_sufficient(
        _context(answer_quality=_answer_quality(unexpected_pages=[99]))
    )

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY


def test_generic_strategy_is_sufficient_when_clause_coverage_is_absent() -> None:
    """A single-clause question never computes clause_coverage (stays
    `None`) -- must be completely inert for every existing caller."""
    strategy = GenericEvidenceSufficiencyStrategy()

    verdict = strategy.is_answer_sufficient(_context(clause_coverage=None))

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT


def test_generic_strategy_is_sufficient_when_all_clauses_are_covered() -> None:
    strategy = GenericEvidenceSufficiencyStrategy()
    clause_coverage = MultiClauseCoverageResult(
        clauses=(
            ClauseCoverage(clause="what is the pressure", is_covered=True),
            ClauseCoverage(clause="what is the temperature", is_covered=True),
        )
    )

    verdict = strategy.is_answer_sufficient(
        _context(clause_coverage=clause_coverage)
    )

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT


def test_generic_strategy_is_insufficient_when_a_clause_is_uncovered() -> None:
    strategy = GenericEvidenceSufficiencyStrategy()
    clause_coverage = MultiClauseCoverageResult(
        clauses=(
            ClauseCoverage(clause="what is the pressure", is_covered=True),
            ClauseCoverage(clause="what is the temperature", is_covered=False),
        )
    )

    verdict = strategy.is_answer_sufficient(
        _context(clause_coverage=clause_coverage)
    )

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY
    assert "what is the temperature" in verdict.missing_information
