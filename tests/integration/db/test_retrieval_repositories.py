from src.domain.common import ChunkType, DocumentType, SourceLocation
from src.domain.document import (
    Document,
    DocumentChunk,
    DocumentGraph,
    DocumentHashes,
    DocumentSection,
)
from src.infrastructure.db.repositories.retrieval import (
    SqlAlchemyVectorMappingRepository,
    SqlKeywordRepository,
)


def test_vector_mapping_repository_saves_and_gets_qdrant_point_id(
    db_uow,
    db_session,
    sample_document_graph,
    document_id,
    chunk_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    repository = SqlAlchemyVectorMappingRepository(db_session)

    repository.save_mapping(
        vector_id="vector_001",
        document_id=document_id,
        chunk_id=chunk_id,
        qdrant_collection="document_chunks",
        qdrant_point_id="qdrant_point_001",
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_text_hash="hash_001",
    )
    db_session.commit()

    point_id = repository.get_qdrant_point_id(chunk_id)

    assert point_id == "qdrant_point_001"


def test_vector_mapping_repository_lists_chunk_ids_by_document(
    db_uow,
    db_session,
    sample_document_graph,
    document_id,
    chunk_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    repository = SqlAlchemyVectorMappingRepository(db_session)

    repository.save_mapping(
        vector_id="vector_001",
        document_id=document_id,
        chunk_id=chunk_id,
        qdrant_collection="document_chunks",
        qdrant_point_id="qdrant_point_001",
        embedding_model="BAAI/bge-small-en-v1.5",
    )
    db_session.commit()

    chunk_ids = repository.list_chunk_ids_by_document(document_id)

    assert chunk_ids == [chunk_id]


def test_sql_keyword_repository_searches_chunks(
    db_uow,
    db_session,
    sample_document_graph,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    repository = SqlKeywordRepository(db_session)

    results = repository.search_chunks(
        query="hydraulic filter",
        limit=5,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "chunk_001"
    assert results[0].retrieval_source == "sql_keyword"


def test_sql_keyword_repository_finds_merged_chunk_via_touched_section_ids(
    db_uow,
    db_session,
) -> None:
    # Regression: a chunk merged from sibling subsections (see
    # SectionMergePolicy) displays a collapsed primary section_path but is
    # persisted with section_ids listing every subsection it drew content
    # from. ChunkMapper denormalizes those into section_ids_text so SQL
    # keyword search's section-match bonus (not just content ilike) can
    # still find/score it for a query naming one of the folded-in
    # subsections.
    document_id = "doc_merge_001"
    graph = DocumentGraph(
        document=Document(
            document_id=document_id,
            file_name="contract.pdf",
            file_path="data/input/contract.pdf",
            hashes=DocumentHashes(file_hash="fh_merge", content_hash="ch_merge"),
            title="Service Contract",
            document_type=DocumentType.MANUAL,
        )
    )
    graph.add_section(
        DocumentSection(
            section_id="sec_general",
            document_id=document_id,
            title="1 General",
            level=1,
            section_path=["1 General"],
        )
    )
    graph.add_section(
        DocumentSection(
            section_id="sec_18",
            document_id=document_id,
            title="1.8 Liability and Warranty",
            level=2,
            parent_section_id="sec_general",
            section_path=["1 General", "1.8 Liability and Warranty"],
        )
    )
    graph.add_chunk(
        DocumentChunk(
            chunk_id="chunk_merged",
            document_id=document_id,
            section_id="sec_general",
            content="General provisions apply. Warranty coverage is limited to defects.",
            chunk_type=ChunkType.GENERAL,
            section_path=["1 General"],
            section_ids=["sec_general", "sec_18"],
            source=SourceLocation(page_start=1, page_end=1),
        )
    )
    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    repository = SqlKeywordRepository(db_session)

    results = repository.search_chunks(query="liability and warranty", limit=5)

    assert len(results) == 1
    assert results[0].chunk_id == "chunk_merged"
    assert results[0].metadata["sql_touched_section_match"] == "true"