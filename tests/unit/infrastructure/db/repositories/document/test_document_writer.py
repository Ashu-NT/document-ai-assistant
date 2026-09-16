from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.domain.common import ChunkType, ElementType, SourceLocation
from src.domain.document import (
    Document,
    DocumentChunk,
    DocumentGraph,
    DocumentHashes,
    DocumentSection,
)
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceEvidence,
)
from src.domain.document.entities.identifier import Identifier
from src.domain.elements import CanonicalElement
from src.infrastructure.db.orm_models import (
    ChunkCrossReferenceORM,
    ChunkORM,
    CrossReferenceEvidenceORM,
    ElementORM,
    IdentifierORM,
    SectionORM,
)
from src.infrastructure.db.repositories.document.document_graph_reader import (
    DocumentGraphReader,
)
from src.infrastructure.db.repositories.document.document_writer import DocumentWriter
from src.infrastructure.db.schema_management import ensure_database_schema


def _make_engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    ensure_database_schema(engine)
    return engine


def _make_graph(*, section_title: str, chunk_content: str) -> DocumentGraph:
    document = Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(file_hash="hash_1", content_hash="content_1"),
    )
    graph = DocumentGraph(document=document)
    graph.add_section(
        DocumentSection(
            section_id="sec_1",
            document_id="doc_001",
            title=section_title,
        )
    )
    graph.add_element(
        CanonicalElement(
            element_id="el_1",
            document_id="doc_001",
            element_type=ElementType.TEXT,
            text="Some element text.",
            parent_section_id="sec_1",
        )
    )
    graph.add_chunk(
        DocumentChunk(
            chunk_id="chunk_1",
            document_id="doc_001",
            section_id="sec_1",
            content=chunk_content,
            chunk_type=ChunkType.GENERAL,
        )
    )
    graph.identifiers["id_1"] = Identifier(
        identifier_id="id_1",
        document_id="doc_001",
        raw_value="HP-001",
        chunk_id="chunk_1",
    )
    return graph


def _add_annex_cross_reference(graph: DocumentGraph) -> None:
    graph.add_chunk(
        DocumentChunk(
            chunk_id="chunk_2",
            document_id="doc_001",
            section_id="sec_1",
            content="8.2 Annex 2",
            chunk_type=ChunkType.GENERAL,
        )
    )
    graph.add_cross_reference(
        ChunkCrossReference(
            cross_reference_id="xref_annex_1",
            document_id="doc_001",
            source_chunk_id="chunk_1",
            target_chunk_id="chunk_2",
            reference_type=ChunkCrossReferenceType.ANNEX_REFERENCE,
            matched_text="Refer to Annex 2",
            target_annex_label="Annex 2",
            resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
            confidence_score=0.85,
        )
    )
    graph.add_cross_reference_evidence(
        CrossReferenceEvidence(
            evidence_id="xref_evidence_annex_1",
            document_id="doc_001",
            source_chunk_id="chunk_1",
            reference_type=ChunkCrossReferenceType.ANNEX_REFERENCE,
            matched_text="Refer to Annex 2",
            target_annex_label="Annex 2",
            target_chunk_id="chunk_2",
            resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
            confidence_score=0.85,
        )
    )


def test_save_and_read_document_graph_round_trips_annex_cross_reference_target_label() -> (
    None
):
    engine = _make_engine()
    graph = _make_graph(section_title="Intro", chunk_content="Refer to Annex 2 for details.")
    _add_annex_cross_reference(graph)

    with Session(engine) as session:
        DocumentWriter(session).save_document_graph(graph)
        session.commit()

        assert session.execute(
            select(ChunkCrossReferenceORM.target_annex_label).where(
                ChunkCrossReferenceORM.id == "xref_annex_1"
            )
        ).scalar_one() == "Annex 2"
        assert session.execute(
            select(CrossReferenceEvidenceORM.target_annex_label).where(
                CrossReferenceEvidenceORM.id == "xref_evidence_annex_1"
            )
        ).scalar_one() == "Annex 2"

    with Session(engine) as session:
        read_back = DocumentGraphReader(session).get_document_graph("doc_001")

        assert read_back is not None
        canonical = read_back.cross_references["xref_annex_1"]
        assert canonical.reference_type == ChunkCrossReferenceType.ANNEX_REFERENCE
        assert canonical.target_annex_label == "Annex 2"


def test_save_document_graph_persists_null_target_annex_label_for_non_annex_reference() -> (
    None
):
    """Proves the new nullable column doesn't break persistence of reference
    types that never populate an annex label (PAGE_REFERENCE here)."""
    engine = _make_engine()
    graph = _make_graph(section_title="Intro", chunk_content="See page 42.")
    graph.add_cross_reference(
        ChunkCrossReference(
            cross_reference_id="xref_page_1",
            document_id="doc_001",
            source_chunk_id="chunk_1",
            target_chunk_id=None,
            reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
            matched_text="page 42",
            target_page=42,
            resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
            confidence_score=0.0,
        )
    )
    graph.add_cross_reference_evidence(
        CrossReferenceEvidence(
            evidence_id="xref_evidence_page_1",
            document_id="doc_001",
            source_chunk_id="chunk_1",
            reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
            matched_text="page 42",
            target_page=42,
            target_chunk_id=None,
            resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
            confidence_score=0.0,
        )
    )

    with Session(engine) as session:
        DocumentWriter(session).save_document_graph(graph)
        session.commit()

        assert session.execute(
            select(ChunkCrossReferenceORM.target_annex_label).where(
                ChunkCrossReferenceORM.id == "xref_page_1"
            )
        ).scalar_one() is None
        assert session.execute(
            select(CrossReferenceEvidenceORM.target_annex_label).where(
                CrossReferenceEvidenceORM.id == "xref_evidence_page_1"
            )
        ).scalar_one() is None


def test_save_document_graph_persists_all_entities() -> None:
    engine = _make_engine()
    graph = _make_graph(section_title="Intro", chunk_content="First version.")

    with Session(engine) as session:
        DocumentWriter(session).save_document_graph(graph)
        session.commit()

        assert session.execute(
            select(SectionORM.title).where(SectionORM.id == "sec_1")
        ).scalar_one() == "Intro"
        assert session.execute(
            select(ChunkORM.content).where(ChunkORM.id == "chunk_1")
        ).scalar_one() == "First version."
        assert session.execute(
            select(ElementORM.id).where(ElementORM.id == "el_1")
        ).scalar_one() == "el_1"
        assert session.execute(
            select(IdentifierORM.raw_value).where(IdentifierORM.id == "id_1")
        ).scalar_one() == "HP-001"


def test_replace_document_graph_updates_existing_rows_without_duplicating() -> None:
    engine = _make_engine()

    with Session(engine) as session:
        DocumentWriter(session).save_document_graph(
            _make_graph(section_title="Intro", chunk_content="First version.")
        )
        session.commit()

    with Session(engine) as session:
        DocumentWriter(session).replace_document_graph(
            _make_graph(section_title="Introduction (revised)", chunk_content="Second version.")
        )
        session.commit()

        section_rows = session.execute(select(SectionORM.id, SectionORM.title)).all()
        chunk_rows = session.execute(select(ChunkORM.id, ChunkORM.content)).all()

        assert section_rows == [("sec_1", "Introduction (revised)")]
        assert chunk_rows == [("chunk_1", "Second version.")]
