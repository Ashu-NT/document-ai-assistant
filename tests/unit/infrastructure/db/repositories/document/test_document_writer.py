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
from src.domain.document.entities.identifier import Identifier
from src.domain.elements import CanonicalElement
from src.infrastructure.db.orm_models import (
    ChunkORM,
    ElementORM,
    IdentifierORM,
    SectionORM,
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
