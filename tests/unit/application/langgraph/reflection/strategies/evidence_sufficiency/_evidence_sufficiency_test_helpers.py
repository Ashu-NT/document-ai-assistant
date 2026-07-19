from src.application.langgraph.reflection.models import AnswerQuality, EvidenceQuality
from src.application.langgraph.reflection.strategies.evidence_sufficiency import (
    EvidenceSufficiencyContext,
)


def make_answer_quality(**overrides) -> AnswerQuality:
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


def make_evidence_quality(**overrides) -> EvidenceQuality:
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


def make_context(**overrides) -> EvidenceSufficiencyContext:
    defaults = dict(
        question="What is the operating pressure?",
        answer_text="The operating pressure is 6 bar.",
        answer_intent="specification_summary",
        selected_document_id="doc_1",
        approved_chunks=[{"document_id": "doc_1", "content": "operating pressure 6 bar"}],
        rejected_chunks=[],
        evidence_quality=make_evidence_quality(),
        answer_quality=make_answer_quality(),
    )
    defaults.update(overrides)
    return EvidenceSufficiencyContext(**defaults)
