from src.application.services.answer_generation.coverage import (
    BEST_EFFORT_SUMMARY,
    COMPARISON,
    EXHAUSTIVE_LIST,
    ORDERED_PROCEDURE,
    SINGLE_FACT,
    resolve_coverage_requirement,
)
from src.application.services.answer_generation.intent.answer_intent import AnswerIntent


def test_resolve_maps_procedure_steps_to_ordered_procedure() -> None:
    assert (
        resolve_coverage_requirement(
            answer_intent=AnswerIntent.PROCEDURE_STEPS,
            question="How do I replace the hydraulic filter?",
        )
        == ORDERED_PROCEDURE
    )


def test_resolve_maps_identifier_lookup_to_exhaustive_list() -> None:
    assert (
        resolve_coverage_requirement(
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            question="What is the part number for the filter?",
        )
        == EXHAUSTIVE_LIST
    )


def test_resolve_maps_specification_summary_to_single_fact() -> None:
    assert (
        resolve_coverage_requirement(
            answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
            question="What is the operating pressure?",
        )
        == SINGLE_FACT
    )


def test_resolve_defaults_unmapped_intents_to_best_effort_summary() -> None:
    assert (
        resolve_coverage_requirement(
            answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
            question="What is the maintenance schedule?",
        )
        == BEST_EFFORT_SUMMARY
    )
    assert (
        resolve_coverage_requirement(answer_intent=None, question="Tell me about it.")
        == BEST_EFFORT_SUMMARY
    )


def test_resolve_comparison_wording_overrides_the_intent_default() -> None:
    assert (
        resolve_coverage_requirement(
            answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
            question="Compare the operating pressure of model A vs model B.",
        )
        == COMPARISON
    )


def test_resolve_exhaustive_list_wording_overrides_a_single_fact_intent() -> None:
    """A SPECIFICATION_SUMMARY intent alone would default to SINGLE_FACT,
    but "list all" wording demands more completeness than that default --
    question wording can only ever raise the bar, never lower it."""
    assert (
        resolve_coverage_requirement(
            answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
            question="List all of the technical specifications.",
        )
        == EXHAUSTIVE_LIST
    )


def test_resolve_handles_missing_question_text() -> None:
    assert (
        resolve_coverage_requirement(answer_intent=AnswerIntent.GENERAL, question=None)
        == BEST_EFFORT_SUMMARY
    )
