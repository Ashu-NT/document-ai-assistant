from sqlalchemy import delete, select

from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceEvidence,
    CrossReferenceReconciliationOutcome,
)
from src.infrastructure.db.orm_models import ChunkCrossReferenceORM, CrossReferenceEvidenceORM


def _add_confirmed_pair(graph, *, document_id: str, source_chunk_id: str, target_chunk_id: str):
    canonical = ChunkCrossReference(
        cross_reference_id="xref_canonical_1",
        document_id=document_id,
        source_chunk_id=source_chunk_id,
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        matched_text="pdf_link_annotation",
        target_chunk_id=target_chunk_id,
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.9,
        reconciliation_outcome=CrossReferenceReconciliationOutcome.CONFIRMED,
    )
    graph.add_cross_reference(canonical)

    fuzzy_evidence = CrossReferenceEvidence(
        evidence_id="xref_evidence_fuzzy_1",
        document_id=document_id,
        source_chunk_id=source_chunk_id,
        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
        matched_text="chap. 3.1",
        target_chunk_id=target_chunk_id,
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.85,
        reconciliation_outcome=CrossReferenceReconciliationOutcome.CONFIRMED,
        reconciliation_group_id="xref_evidence_group_1",
        canonical_cross_reference_id=canonical.cross_reference_id,
    )
    native_evidence = CrossReferenceEvidence(
        evidence_id="xref_evidence_native_1",
        document_id=document_id,
        source_chunk_id=source_chunk_id,
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        matched_text="pdf_link_annotation",
        target_chunk_id=target_chunk_id,
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.9,
        reconciliation_outcome=CrossReferenceReconciliationOutcome.CONFIRMED,
        reconciliation_group_id="xref_evidence_group_1",
        canonical_cross_reference_id=canonical.cross_reference_id,
    )
    graph.add_cross_reference_evidence(fuzzy_evidence)
    graph.add_cross_reference_evidence(native_evidence)
    return canonical, [fuzzy_evidence, native_evidence]


def test_save_document_graph_persists_canonical_row_and_both_evidence_rows(
    db_uow, seed_document_with_chunks, document_id: str, db_session
) -> None:
    seed_document_with_chunks(["chunk_source", "chunk_target"])
    graph = db_uow.documents.get_document_graph(document_id)
    _add_confirmed_pair(
        graph,
        document_id=document_id,
        source_chunk_id="chunk_source",
        target_chunk_id="chunk_target",
    )

    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    canonical_rows = db_session.execute(
        select(ChunkCrossReferenceORM).where(
            ChunkCrossReferenceORM.document_id == document_id
        )
    ).scalars().all()
    assert len(canonical_rows) == 1
    assert canonical_rows[0].reconciliation_outcome == "confirmed"

    evidence_rows = db_session.execute(
        select(CrossReferenceEvidenceORM).where(
            CrossReferenceEvidenceORM.document_id == document_id
        )
    ).scalars().all()
    assert len(evidence_rows) == 2
    assert {row.reconciliation_group_id for row in evidence_rows} == {
        "xref_evidence_group_1"
    }
    assert all(
        row.canonical_cross_reference_id == "xref_canonical_1" for row in evidence_rows
    )


def test_deleting_the_document_cascades_evidence_rows(
    db_uow, seed_document_with_chunks, document_id: str, db_session
) -> None:
    seed_document_with_chunks(["chunk_source", "chunk_target"])
    graph = db_uow.documents.get_document_graph(document_id)
    _add_confirmed_pair(
        graph,
        document_id=document_id,
        source_chunk_id="chunk_source",
        target_chunk_id="chunk_target",
    )
    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    db_uow.documents.delete_document(document_id)
    db_uow.commit()

    remaining = db_session.execute(
        select(CrossReferenceEvidenceORM).where(
            CrossReferenceEvidenceORM.document_id == document_id
        )
    ).scalars().all()
    assert remaining == []


def test_replacing_the_document_graph_deletes_stale_evidence_and_reinserts_fresh_rows(
    db_uow, seed_document_with_chunks, document_id: str, db_session
) -> None:
    seed_document_with_chunks(["chunk_source", "chunk_target"])
    graph = db_uow.documents.get_document_graph(document_id)
    _add_confirmed_pair(
        graph,
        document_id=document_id,
        source_chunk_id="chunk_source",
        target_chunk_id="chunk_target",
    )
    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    fresh_graph = db_uow.documents.get_document_graph(document_id)
    fresh_evidence = CrossReferenceEvidence(
        evidence_id="xref_evidence_fresh_1",
        document_id=document_id,
        source_chunk_id="chunk_source",
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        matched_text="(see page 41)",
        target_chunk_id=None,
        resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
        confidence_score=0.0,
    )
    fresh_graph.add_cross_reference_evidence(fresh_evidence)

    db_uow.documents.replace_document_graph(fresh_graph)
    db_uow.commit()

    evidence_rows = db_session.execute(
        select(CrossReferenceEvidenceORM).where(
            CrossReferenceEvidenceORM.document_id == document_id
        )
    ).scalars().all()
    assert [row.id for row in evidence_rows] == ["xref_evidence_fresh_1"]


def test_deleting_the_canonical_row_directly_sets_evidence_association_to_null(
    db_uow, seed_document_with_chunks, document_id: str, db_session
) -> None:
    """The evidence row (matched_text, resolution_status, provenance) is
    still worth keeping for audit even if the canonical row it once fed is
    later removed - ON DELETE SET NULL, not CASCADE."""
    seed_document_with_chunks(["chunk_source", "chunk_target"])
    graph = db_uow.documents.get_document_graph(document_id)
    canonical, _ = _add_confirmed_pair(
        graph,
        document_id=document_id,
        source_chunk_id="chunk_source",
        target_chunk_id="chunk_target",
    )
    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    db_session.execute(
        delete(ChunkCrossReferenceORM).where(
            ChunkCrossReferenceORM.id == canonical.cross_reference_id
        )
    )
    db_session.commit()

    evidence_rows = db_session.execute(
        select(CrossReferenceEvidenceORM).where(
            CrossReferenceEvidenceORM.document_id == document_id
        )
    ).scalars().all()
    assert len(evidence_rows) == 2
    assert all(row.canonical_cross_reference_id is None for row in evidence_rows)
