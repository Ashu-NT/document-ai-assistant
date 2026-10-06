from src.application.workflows.extraction.response.merging.safety_warning_merger import (
    merge_safety_warnings,
)
from src.domain.extraction import ExtractionResult, SafetyWarning


def _warning(
    *,
    warning_id: str,
    message: str,
    warning_type: str = "warning",
    component_name: str | None = None,
    source_chunk_id: str | None = None,
    confidence_score: float | None = None,
) -> SafetyWarning:
    return SafetyWarning(
        safety_warning_id=warning_id,
        document_id="doc_001",
        warning_type=warning_type,
        message=message,
        component_name=component_name,
        source_chunk_id=source_chunk_id,
        confidence_score=confidence_score,
    )


def _result(*warnings: SafetyWarning) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_001",
        document_id="doc_001",
        safety_warnings=list(warnings),
    )


def test_genuinely_distinct_warnings_are_not_collapsed() -> None:
    crushing = _warning(
        warning_id="sw_1",
        message="Components are moving or rotating. Risk of crushing.",
    )
    fire = _warning(
        warning_id="sw_2",
        message="Fuels are combustible and explosive. Risk of fire and explosion.",
    )
    burns = _warning(
        warning_id="sw_3",
        message="Hot components/surfaces. Risk of burns.",
    )

    merged = merge_safety_warnings([_result(crushing, fire, burns)])

    assert len(merged) == 3
    assert {warning.message for warning in merged} == {
        crushing.message,
        fire.message,
        burns.message,
    }


def test_identical_warning_messages_from_different_calls_still_dedupe() -> None:
    # Same warning text extracted independently from two specialized calls
    # over overlapping/adjacent chunks (or two attempts) must still collapse
    # into one entity - the atomicity fix must not disable real dedup.
    first = _warning(
        warning_id="sw_1",
        message="Risk of crushing, danger of parts of the body being caught or pulled in!",
        component_name=None,
        source_chunk_id=None,
        confidence_score=0.8,
    )
    second = _warning(
        warning_id="sw_2",
        message="Risk of crushing, danger of parts of the body being caught or pulled in!",
        component_name="Fuel filter",
        source_chunk_id="chunk_163",
        confidence_score=0.9,
    )

    merged = merge_safety_warnings([_result(first), _result(second)])

    assert len(merged) == 1
    kept = merged[0]
    assert kept.component_name == "Fuel filter"
    assert kept.source_chunk_id == "chunk_163"
    assert kept.confidence_score == 0.9


def test_dedup_is_whitespace_and_case_insensitive_but_not_content_insensitive() -> None:
    padded = _warning(warning_id="sw_1", message="  Risk of crushing!  ")
    recased = _warning(warning_id="sw_2", message="RISK OF CRUSHING!")
    different = _warning(warning_id="sw_3", message="Risk of fire and explosion!")

    merged = merge_safety_warnings([_result(padded, recased, different)])

    assert len(merged) == 2
