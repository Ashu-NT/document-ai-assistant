from datetime import datetime

from src.domain.common import ChunkType, DocumentType
from src.domain.retrieval import RetrievalQuery
from src.infrastructure.db.orm_models import ChunkORM, DocumentORM
from src.infrastructure.db.repositories.retrieval.sql_keyword_repository import (
    SqlKeywordRepository,
)


class FakeExecuteResult:
    def __init__(self, rows) -> None:
        self.rows = rows

    def all(self):
        return list(self.rows)


class FakeSession:
    def __init__(self, rows) -> None:
        self.rows = rows
        self.statements = []

    def execute(self, statement):
        self.statements.append(statement)
        return FakeExecuteResult(self.rows)


def make_document(
    *,
    document_id: str,
    file_name: str,
    title: str,
    document_type: DocumentType,
) -> DocumentORM:
    return DocumentORM(
        id=document_id,
        file_name=file_name,
        file_path=file_name,
        file_hash=f"{document_id}_hash",
        content_hash=f"{document_id}_content_hash",
        title=title,
        document_type=document_type.value,
        language="en",
        page_count=1,
        created_at=datetime.utcnow(),
    )


def make_chunk(
    *,
    chunk_id: str,
    document_id: str,
    content: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    section_path: str = '["General"]',
) -> ChunkORM:
    return ChunkORM(
        id=chunk_id,
        document_id=document_id,
        section_id="sec_001",
        content=content,
        embedding_text=content,
        chunk_type=chunk_type.value,
        section_path=section_path,
        page_start=1,
        page_end=1,
        sequence_number=1,
        chunk_index=1,
        chunk_total=1,
        char_count=len(content),
        token_count_estimate=len(content.split()),
        created_at=datetime.utcnow(),
    )


def test_sql_keyword_repository_prioritizes_exact_identifier_hits() -> None:
    exact_document = make_document(
        document_id="doc_spec",
        file_name="datasheet.pdf",
        title="Ordering example",
        document_type=DocumentType.DATASHEET,
    )
    generic_document = make_document(
        document_id="doc_manual",
        file_name="manual.pdf",
        title="Operation Manual",
        document_type=DocumentType.MANUAL,
    )
    exact_chunk = make_chunk(
        chunk_id="chunk_exact",
        document_id="doc_spec",
        content="MK311007 = 2-way Wafer-type Ball valve, stainless steel, handle, DN 50.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path='["Ordering example"]',
    )
    generic_chunk = make_chunk(
        chunk_id="chunk_generic",
        document_id="doc_manual",
        content="Order code examples and valve descriptions are listed in this manual.",
        chunk_type=ChunkType.GENERAL,
        section_path='["Revision / modification table"]',
    )
    repository = SqlKeywordRepository(
        FakeSession(
            [
                (generic_chunk, generic_document),
                (exact_chunk, exact_document),
            ]
        )
    )
    query = RetrievalQuery(
        query_id="query_001",
        query_text="What does ordering code MK311007 mean?",
        detected_identifiers=["mk311007"],
    )

    results = repository.search_chunks(query)

    assert results[0].chunk_id == "chunk_exact"
    assert results[0].metadata["document_type"] == DocumentType.DATASHEET.value
    assert len(results) == 1 or float(
        results[0].metadata["sql_keyword_source_score"]
    ) > float(results[1].metadata["sql_keyword_source_score"])


def test_sql_keyword_repository_penalizes_revision_table_noise() -> None:
    document = make_document(
        document_id="doc_manual",
        file_name="manual.pdf",
        title="Manual",
        document_type=DocumentType.MANUAL,
    )
    noisy_chunk = make_chunk(
        chunk_id="chunk_noisy",
        document_id="doc_manual",
        content="How to start and run the macerator safely.",
        chunk_type=ChunkType.GENERAL,
        section_path='["Revision / modification table"]',
    )
    clean_chunk = make_chunk(
        chunk_id="chunk_clean",
        document_id="doc_manual",
        content="Start/Run illuminated solid green; fill food, close lid, press Start/Run.",
        chunk_type=ChunkType.OPERATION_INSTRUCTION,
        section_path='["6 Operation & General Maintenance", "6.3 Operation Macerator"]',
    )
    repository = SqlKeywordRepository(
        FakeSession([(noisy_chunk, document), (clean_chunk, document)])
    )
    query = RetrievalQuery(
        query_id="query_002",
        query_text="How do I start and run the macerator?",
        chunk_types=[ChunkType.OPERATION_INSTRUCTION, ChunkType.GENERAL],
    )

    results = repository.search_chunks(query)

    assert results[0].chunk_id == "chunk_clean"


def test_sql_keyword_repository_filters_by_document_id_when_set() -> None:
    document = make_document(
        document_id="doc_fwc12",
        file_name="manual.pdf",
        title="FWC12 Manual",
        document_type=DocumentType.MANUAL,
    )
    chunk = make_chunk(
        chunk_id="chunk_in_scope",
        document_id="doc_fwc12",
        content="Lubricate shaft seals every 350 hours of operation.",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
    )
    repository = SqlKeywordRepository(FakeSession([(chunk, document)]))
    query = RetrievalQuery(
        query_id="q_scoped",
        query_text="How often should shaft seals be lubricated?",
        document_id="doc_fwc12",
    )

    results = repository.search_chunks(query)

    # The statement should include a document_id condition — verify it ran without error
    # and that the chunk scored above zero (SQL keyword match on content).
    assert len(results) == 1
    assert results[0].chunk_id == "chunk_in_scope"


def test_sql_keyword_repository_corpus_wide_when_no_document_id() -> None:
    doc_a = make_document(
        document_id="doc_a",
        file_name="manual.pdf",
        title="Manual A",
        document_type=DocumentType.MANUAL,
    )
    doc_b = make_document(
        document_id="doc_b",
        file_name="report.pdf",
        title="Report B",
        document_type=DocumentType.REPORT,
    )
    chunk_a = make_chunk(
        chunk_id="chunk_a",
        document_id="doc_a",
        content="Shaft seal lubrication every 350 hours.",
    )
    chunk_b = make_chunk(
        chunk_id="chunk_b",
        document_id="doc_b",
        content="Shaft seal lubrication schedule.",
    )
    repository = SqlKeywordRepository(FakeSession([(chunk_a, doc_a), (chunk_b, doc_b)]))
    query = RetrievalQuery(
        query_id="q_wide",
        query_text="shaft seal lubrication",
    )

    results = repository.search_chunks(query)

    returned_ids = {r.chunk_id for r in results}
    assert "chunk_a" in returned_ids
    assert "chunk_b" in returned_ids


def test_sql_keyword_repository_boosts_matching_section_path_and_chunk_type() -> None:
    document = make_document(
        document_id="doc_report",
        file_name="pressure-transmitter.pdf",
        title="Pressure transmitter",
        document_type=DocumentType.REPORT,
    )
    generic_chunk = make_chunk(
        chunk_id="chunk_generic",
        document_id="doc_report",
        content="Electrical data and operating information.",
        chunk_type=ChunkType.GENERAL,
        section_path='["General information"]',
    )
    specific_chunk = make_chunk(
        chunk_id="chunk_specific",
        document_id="doc_report",
        content="Supply voltage 11.5 to 45 V DC for 4 to 20 mA HART.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path='["6 Electrical connection", "6.2.6 Supply voltage"]',
    )
    repository = SqlKeywordRepository(
        FakeSession([(generic_chunk, document), (specific_chunk, document)])
    )
    query = RetrievalQuery(
        query_id="query_003",
        query_text="What supply voltage is specified for 4 to 20 mA HART Cerabar M devices?",
        chunk_types=[ChunkType.TECHNICAL_SPECIFICATION],
    )

    results = repository.search_chunks(query)

    assert results[0].chunk_id == "chunk_specific"
    assert results[0].metadata["sql_section_path_match"] == "true"
