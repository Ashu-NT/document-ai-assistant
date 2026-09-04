from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.pdf_link_cross_reference_linker import (
    PdfLinkLinkingDiagnostics,
    PdfLinkLinkingResult,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.reconciliation.cross_reference_reconciliation_service import (
    CrossReferenceReconciliationService,
)
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceReconciliationOutcome,
)
from src.shared.ids import IdGenerator


def xref(
    *,
    reference_type: ChunkCrossReferenceType,
    source_chunk_id: str,
    target_chunk_id: str | None,
    resolution_status: ChunkCrossReferenceResolutionStatus,
    matched_text: str = "matched",
) -> ChunkCrossReference:
    return ChunkCrossReference(
        cross_reference_id="stub",
        document_id="doc_001",
        source_chunk_id=source_chunk_id,
        reference_type=reference_type,
        matched_text=matched_text,
        target_chunk_id=target_chunk_id,
        resolution_status=resolution_status,
        confidence_score=0.9,
    )


def native_result(*references: ChunkCrossReference) -> PdfLinkLinkingResult:
    return PdfLinkLinkingResult(
        references=list(references), diagnostics=PdfLinkLinkingDiagnostics()
    )


def _service() -> CrossReferenceReconciliationService:
    return CrossReferenceReconciliationService(id_generator=IdGenerator())


def test_confirmed_when_fuzzy_and_native_agree_on_target_yields_one_canonical_row() -> (
    None
):
    fuzzy = xref(
        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    native = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[fuzzy], native_result=native_result(native)
    )

    assert result.diagnostics.confirmed_count == 1
    assert len(result.canonical_references) == 1
    canonical = result.canonical_references[0]
    assert canonical.reconciliation_outcome == CrossReferenceReconciliationOutcome.CONFIRMED
    assert canonical.target_chunk_id == "c2"

    assert len(result.evidence) == 2
    group_ids = {evidence.reconciliation_group_id for evidence in result.evidence}
    assert len(group_ids) == 1
    canonical_ids = {evidence.canonical_cross_reference_id for evidence in result.evidence}
    assert canonical_ids == {canonical.cross_reference_id}


def test_confirmed_prefers_section_reference_shape_but_always_attaches_native_provenance() -> (
    None
):
    section_fuzzy = xref(
        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    native = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[section_fuzzy],
        native_result=native_result(native),
    )

    canonical = result.canonical_references[0]
    assert canonical.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE

    page_fuzzy = xref(
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        source_chunk_id="c3",
        target_chunk_id="c4",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    native_2 = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c3",
        target_chunk_id="c4",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    result_2 = _service().reconcile(
        location_type_fuzzy_references=[page_fuzzy], native_result=native_result(native_2)
    )
    canonical_2 = result_2.canonical_references[0]
    assert canonical_2.reference_type == ChunkCrossReferenceType.PDF_LINK_REFERENCE


def test_accepted_textual_when_explicit_section_reference_conflicts_with_native() -> None:
    fuzzy = xref(
        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    native = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c3",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[fuzzy], native_result=native_result(native)
    )

    assert result.diagnostics.accepted_textual_count == 1
    canonical = result.canonical_references[0]
    assert canonical.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE
    assert canonical.target_chunk_id == "c2"
    assert (
        canonical.reconciliation_outcome
        == CrossReferenceReconciliationOutcome.ACCEPTED_TEXTUAL
    )


def test_accepted_native_when_weak_fuzzy_conflicts_with_unique_native() -> None:
    fuzzy = xref(
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS,
    )
    native = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c3",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[fuzzy], native_result=native_result(native)
    )

    assert result.diagnostics.accepted_native_count == 1
    canonical = result.canonical_references[0]
    assert canonical.reference_type == ChunkCrossReferenceType.PDF_LINK_REFERENCE
    assert canonical.target_chunk_id == "c3"


def test_conflict_when_unique_page_reference_disagrees_with_native_and_yields_no_canonical_row() -> (
    None
):
    fuzzy = xref(
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    native = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c3",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[fuzzy], native_result=native_result(native)
    )

    assert result.diagnostics.conflict_count == 1
    assert result.canonical_references == []
    assert len(result.evidence) == 2
    assert all(
        evidence.reconciliation_outcome == CrossReferenceReconciliationOutcome.CONFLICT
        for evidence in result.evidence
    )
    assert all(
        evidence.canonical_cross_reference_id is None for evidence in result.evidence
    )


def test_multiple_independent_native_candidates_on_one_chunk_with_no_fuzzy_are_not_flagged() -> (
    None
):
    """A chunk can legitimately hold several independent, correctly-resolved
    native links with nothing on the fuzzy side to pair against - this must
    not be treated as unreconcilable ambiguity."""
    native_a = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    native_b = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c3",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[], native_result=native_result(native_a, native_b)
    )

    assert result.diagnostics.unreconciled_multi_candidate_chunks == 0
    assert result.diagnostics.single_source_count == 2
    assert len(result.canonical_references) == 2
    assert {c.target_chunk_id for c in result.canonical_references} == {"c2", "c3"}
    assert all(
        c.reconciliation_outcome == CrossReferenceReconciliationOutcome.SINGLE_SOURCE
        for c in result.canonical_references
    )


def test_unreconciled_multi_candidate_when_both_sides_present_and_unpairable() -> None:
    fuzzy_a = xref(
        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    fuzzy_b = xref(
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c3",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )
    native = xref(
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c4",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[fuzzy_a, fuzzy_b],
        native_result=native_result(native),
    )

    assert result.diagnostics.unreconciled_multi_candidate_chunks == 1
    assert result.canonical_references == []
    assert len(result.evidence) == 3
    assert all(
        evidence.reconciliation_outcome
        == CrossReferenceReconciliationOutcome.UNRECONCILED_MULTI_CANDIDATE
        for evidence in result.evidence
    )
    group_ids = {evidence.reconciliation_group_id for evidence in result.evidence}
    assert len(group_ids) == 1


def test_unresolved_fuzzy_candidate_becomes_evidence_only_with_no_canonical_row() -> None:
    unresolved_fuzzy = xref(
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id=None,
        resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
    )

    result = _service().reconcile(
        location_type_fuzzy_references=[unresolved_fuzzy], native_result=None
    )

    assert result.canonical_references == []
    assert len(result.evidence) == 1
    assert (
        result.evidence[0].reconciliation_outcome
        == CrossReferenceReconciliationOutcome.SINGLE_SOURCE
    )
    assert result.evidence[0].canonical_cross_reference_id is None
    assert result.diagnostics.single_source_count == 1


def test_single_fuzzy_candidate_with_no_native_result_passes_through_as_single_source() -> (
    None
):
    fuzzy = xref(
        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
        source_chunk_id="c1",
        target_chunk_id="c2",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
    )

    result = _service().reconcile(location_type_fuzzy_references=[fuzzy], native_result=None)

    assert len(result.canonical_references) == 1
    canonical = result.canonical_references[0]
    assert canonical.target_chunk_id == "c2"
    assert canonical.reconciliation_outcome == CrossReferenceReconciliationOutcome.SINGLE_SOURCE
    assert len(result.evidence) == 1
    assert result.evidence[0].canonical_cross_reference_id == canonical.cross_reference_id
    assert result.diagnostics.single_source_count == 1
