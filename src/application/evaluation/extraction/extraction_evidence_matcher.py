"""Evidence/provenance matching - kept as a SEPARATE dimension from entity
correctness (see task section 10). Primary evidence check is page overlap
(V1's stable, human-reviewable evidence surface); section-heading evidence
is checked only when the fixture declares it. Table association is checked
by presence of a `table_id` only - never `table_row_id`, which the Phase 2B
research confirmed is never populated in production
(`semantic_source_metadata.py` docstring) and is not redesigned here.

Golden evidence NEVER requires an exact chunk id - see
`extraction_evaluation_scope.py`'s docstring for why.
"""

from dataclasses import dataclass

from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractedEvidenceExpectation,
)


@dataclass(frozen=True, slots=True)
class EvidenceInput:
    page_start: int | None = None
    page_end: int | None = None
    section_path: tuple[str, ...] = ()
    table_id: str | None = None


def resolve_evidence_input(
    entity: object,
    *,
    chunk_page_lookup: dict[str, tuple[int | None, int | None]] | None = None,
) -> EvidenceInput:
    """`ExtractedIdentifier` has neither `.source` nor `.source_metadata`
    (confirmed by the Phase 2B research trace) - for it only,
    `chunk_page_lookup` (built by the runner from the real DocumentGraph's
    chunks) resolves evidence via `source_chunk_id`."""
    source_metadata = getattr(entity, "source_metadata", None)
    if source_metadata is not None:
        return EvidenceInput(
            page_start=source_metadata.page_start,
            page_end=source_metadata.page_end,
            section_path=tuple(source_metadata.section_path or ()),
            table_id=source_metadata.table_id,
        )

    source = getattr(entity, "source", None)
    if source is not None and (
        source.page_start is not None or source.page_end is not None
    ):
        return EvidenceInput(page_start=source.page_start, page_end=source.page_end)

    source_chunk_id = getattr(entity, "source_chunk_id", None)
    if source_chunk_id and chunk_page_lookup and source_chunk_id in chunk_page_lookup:
        page_start, page_end = chunk_page_lookup[source_chunk_id]
        return EvidenceInput(page_start=page_start, page_end=page_end)

    return EvidenceInput()


def _pages_overlap(
    expected_start: int | None,
    expected_end: int | None,
    actual_start: int | None,
    actual_end: int | None,
) -> bool | None:
    if expected_start is None and expected_end is None:
        return None
    if actual_start is None and actual_end is None:
        return False
    e_lo = expected_start if expected_start is not None else expected_end
    e_hi = expected_end if expected_end is not None else expected_start
    a_lo = actual_start if actual_start is not None else actual_end
    a_hi = actual_end if actual_end is not None else actual_start
    assert e_lo is not None and e_hi is not None and a_lo is not None and a_hi is not None
    return a_lo <= e_hi and a_hi >= e_lo


@dataclass(frozen=True, slots=True)
class EvidenceMatchResult:
    checked: bool
    page_match: bool | None
    section_match: bool | None
    detail: str

    @property
    def evidence_correct(self) -> bool | None:
        if not self.checked:
            return None
        return self.page_match is not False and self.section_match is not False


def evaluate_evidence(
    expected: ExtractedEvidenceExpectation | None,
    evidence: EvidenceInput,
) -> EvidenceMatchResult:
    if expected is None:
        return EvidenceMatchResult(
            checked=False,
            page_match=None,
            section_match=None,
            detail="no expected evidence declared for this case",
        )

    page_match: bool | None = None
    if expected.page_start is not None or expected.page_end is not None:
        page_match = _pages_overlap(
            expected.page_start, expected.page_end, evidence.page_start, evidence.page_end
        )

    section_match: bool | None = None
    if expected.section_heading:
        section_match = any(
            expected.section_heading.lower() in part.lower()
            for part in evidence.section_path
        )

    detail_parts: list[str] = []
    if page_match is False:
        detail_parts.append(
            f"expected page {expected.page_start}-{expected.page_end}, "
            f"actual {evidence.page_start}-{evidence.page_end}"
        )
    if section_match is False:
        detail_parts.append(
            f"expected section heading {expected.section_heading!r} not found "
            f"in {evidence.section_path}"
        )

    return EvidenceMatchResult(
        checked=True,
        page_match=page_match,
        section_match=section_match,
        detail="; ".join(detail_parts) or "evidence matched",
    )


__all__ = [
    "EvidenceInput",
    "resolve_evidence_input",
    "EvidenceMatchResult",
    "evaluate_evidence",
]
