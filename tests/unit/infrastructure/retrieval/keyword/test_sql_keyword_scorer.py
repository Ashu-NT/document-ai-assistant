"""Unit tests for SqlKeywordScorer source-weighted and normalised scoring."""

from datetime import datetime

import pytest

from src.domain.common import ChunkType, DocumentType
from src.domain.retrieval import RetrievalQuery
from src.infrastructure.db.orm_models import ChunkORM, DocumentORM
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import extract_query_terms
from src.infrastructure.retrieval.keyword.sql_keyword_scorer import SqlKeywordScorer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_document(
    *,
    doc_id: str = "doc_test",
    title: str,
    file_name: str,
    document_type: DocumentType = DocumentType.MANUAL,
) -> DocumentORM:
    return DocumentORM(
        id=doc_id,
        file_name=file_name,
        file_path=file_name,
        file_hash=f"{doc_id}_hash",
        content_hash=f"{doc_id}_content_hash",
        title=title,
        document_type=document_type.value,
        language="en",
        page_count=1,
        created_at=datetime.utcnow(),
    )


def _make_chunk(
    *,
    chunk_id: str = "chunk_test",
    document_id: str = "doc_test",
    content: str,
    embedding_text: str | None = None,
    chunk_type: ChunkType = ChunkType.GENERAL,
    section_path: str = '["General"]',
) -> ChunkORM:
    return ChunkORM(
        id=chunk_id,
        document_id=document_id,
        section_id="sec_001",
        content=content,
        embedding_text=embedding_text or content,
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


def _score(
    chunk: ChunkORM,
    document: DocumentORM,
    query_text: str,
    identifiers: list[str] | None = None,
):
    scorer = SqlKeywordScorer()
    query = RetrievalQuery(
        query_id="q_test",
        query_text=query_text,
        detected_identifiers=identifiers or [],
    )
    terms = extract_query_terms(query_text)
    return scorer.score(
        row=chunk,
        document=document,
        retrieval_query=query,
        query_text=query_text,
        query_terms=terms,
    )


# ---------------------------------------------------------------------------
# 1. Content identifier beats document-title-only identifier
# ---------------------------------------------------------------------------

def test_content_identifier_beats_document_title_identifier() -> None:
    """A chunk that mentions the identifier in its text must outscore one that
    only benefits because the document title carries the identifier."""
    doc_with_id_in_title = _make_document(
        doc_id="doc_titled",
        title="M12345 Pressure Transmitter Manual",
        file_name="m12345_manual.pdf",
    )
    doc_generic = _make_document(
        doc_id="doc_generic",
        title="Generic Sensor Manual",
        file_name="generic_sensor.pdf",
    )

    # Content explicitly mentions the identifier
    chunk_content_match = _make_chunk(
        chunk_id="chunk_content",
        document_id="doc_generic",
        content="M12345 is a 2-wire pressure transmitter with a 4-20 mA digital output.",
    )
    # Identifier absent from content; only present via document title
    chunk_doc_title_only = _make_chunk(
        chunk_id="chunk_title_only",
        document_id="doc_titled",
        content="This chapter describes general installation procedures for all devices.",
    )

    result_content = _score(chunk_content_match, doc_generic, "What is M12345?", ["M12345"])
    result_title = _score(chunk_doc_title_only, doc_with_id_in_title, "What is M12345?", ["M12345"])

    assert result_content.total_score > result_title.total_score, (
        f"content id {result_content.total_score:.2f} should beat doc-title id {result_title.total_score:.2f}"
    )
    assert result_content.metadata["sql_content_identifier_matches"] == "1"
    assert result_title.metadata["sql_content_identifier_matches"] == "0"
    assert result_title.metadata["sql_document_identifier_matches"] == "1"


# ---------------------------------------------------------------------------
# 2. Local section match beats ancestor-path-only match
# ---------------------------------------------------------------------------

def test_local_section_match_beats_ancestor_section_match() -> None:
    """A chunk whose leaf section names match the query must outscore one where
    only the top-level ancestor section contains those terms."""
    doc = _make_document(title="Pump Manual", file_name="pump.pdf")

    # Query terms appear in the local (leaf) section
    chunk_local = _make_chunk(
        content="General procedures apply.",
        section_path='["Electrical", "Connection", "Wiring Diagram"]',
    )
    # Query terms appear only in the ancestor; local section is unrelated
    chunk_ancestor = _make_chunk(
        content="General procedures apply.",
        section_path='["Electrical Connection", "Wiring Overview", "Safety Notes"]',
    )

    query_text = "electrical connection wiring diagram"
    result_local = _score(chunk_local, doc, query_text)
    result_ancestor = _score(chunk_ancestor, doc, query_text)

    assert result_local.total_score > result_ancestor.total_score, (
        f"local match {result_local.total_score:.2f} should beat ancestor match {result_ancestor.total_score:.2f}"
    )
    assert result_local.metadata["sql_local_section_match"] == "true"
    assert result_ancestor.metadata["sql_local_section_match"] == "false"
    # Ancestor match still contributes to the section_path_match flag
    assert result_ancestor.metadata["sql_section_path_match"] == "true"


# ---------------------------------------------------------------------------
# 3. Normalised matching: punctuation / hyphenation / spacing variations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "query_identifier,content",
    [
        # Query without hyphen, content with hyphen
        ("MK311007", "MK-311007 is a 2-way wafer-type ball valve in stainless steel."),
        # Query with hyphen, content without
        ("MK-311007", "MK311007 is a 2-way wafer-type ball valve in stainless steel."),
        # Query with space, content without
        ("MK 311007", "The valve MK311007 is listed in table 4."),
        # Mixed case difference only
        ("mk311007", "MK311007 pressure rating is 16 bar."),
        # Three-segment identifier: "AB-123-XYZ"
        ("AB123XYZ", "Refer to part AB-123-XYZ for replacement."),
    ],
)
def test_normalised_identifier_matching(query_identifier: str, content: str) -> None:
    """Punctuation, hyphenation, spacing, and case differences must not prevent
    identifier matches in chunk content."""
    doc = _make_document(title="Valve Catalog", file_name="valves.pdf")
    chunk = _make_chunk(content=content)

    result = _score(chunk, doc, f"What is {query_identifier}?", [query_identifier])

    assert result.metadata["sql_content_identifier_matches"] == "1", (
        f"identifier '{query_identifier}' should match in content '{content}'"
    )


# ---------------------------------------------------------------------------
# 4. Existing identifier ranking does not regress
# ---------------------------------------------------------------------------

def test_existing_identifier_ranking_does_not_regress() -> None:
    """Chunk whose content contains the exact identifier must outscore a chunk
    that has no identifier evidence anywhere."""
    doc_exact = _make_document(
        doc_id="doc_spec",
        title="Ordering example",
        file_name="datasheet.pdf",
        document_type=DocumentType.DATASHEET,
    )
    doc_generic = _make_document(
        doc_id="doc_manual",
        title="Operation Manual",
        file_name="manual.pdf",
    )

    chunk_exact = _make_chunk(
        chunk_id="chunk_exact",
        document_id="doc_spec",
        content="MK311007 = 2-way Wafer-type Ball valve, stainless steel, handle, DN 50.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path='["Ordering example"]',
    )
    chunk_generic = _make_chunk(
        chunk_id="chunk_generic",
        document_id="doc_manual",
        content="Order code examples and valve descriptions are listed in this manual.",
        section_path='["Revision / modification table"]',
    )

    result_exact = _score(
        chunk_exact, doc_exact, "What does ordering code MK311007 mean?", ["mk311007"]
    )
    result_generic = _score(
        chunk_generic, doc_generic, "What does ordering code MK311007 mean?", ["mk311007"]
    )

    assert result_exact.total_score > result_generic.total_score
    assert result_exact.metadata["sql_content_identifier_matches"] == "1"
    assert result_generic.metadata["sql_content_identifier_matches"] == "0"


# ---------------------------------------------------------------------------
# 5. Existing phrase-match ranking does not regress
# ---------------------------------------------------------------------------

def test_existing_phrase_match_ranking_does_not_regress() -> None:
    """A chunk containing the exact query phrase in its content must outscore
    one that only mentions some of the terms."""
    doc = _make_document(title="Pump Manual", file_name="pump.pdf")

    chunk_phrase = _make_chunk(
        content="To start and run the macerator press the green button and hold for 3 seconds.",
        chunk_type=ChunkType.OPERATION_INSTRUCTION,
        section_path='["6 Operation", "6.3 Macerator Operation"]',
    )
    chunk_partial = _make_chunk(
        content="The macerator requires periodic maintenance and inspection.",
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        section_path='["7 Maintenance"]',
    )

    query_text = "start and run the macerator"
    result_phrase = _score(chunk_phrase, doc, query_text)
    result_partial = _score(chunk_partial, doc, query_text)

    assert result_phrase.total_score > result_partial.total_score
    assert result_phrase.metadata["sql_exact_phrase_match"] == "true"
    assert result_partial.metadata["sql_exact_phrase_match"] == "false"


# ---------------------------------------------------------------------------
# 6. Section identifier match scores between content and document-title
# ---------------------------------------------------------------------------

def test_section_identifier_scores_between_content_and_document() -> None:
    """Section-path identifier hit should score lower than content but higher
    than document-title-only."""
    doc_no_id = _make_document(title="Technical Reference", file_name="ref.pdf")
    doc_with_id_title = _make_document(
        doc_id="doc_with_id",
        title="MK311007 Valve Manual",
        file_name="mk311007.pdf",
    )

    chunk_content = _make_chunk(
        chunk_id="c_content",
        content="MK311007 specifications: 2-way, DN50, PN16.",
    )
    chunk_section = _make_chunk(
        chunk_id="c_section",
        content="See ordering table below.",
        section_path='["MK311007 Ordering Data"]',
    )
    chunk_doc_title = _make_chunk(
        chunk_id="c_doc",
        document_id="doc_with_id",
        content="General installation information.",
    )

    identifier = "MK311007"
    query = "What are the specifications for MK311007?"

    result_content = _score(chunk_content, doc_no_id, query, [identifier])
    result_section = _score(chunk_section, doc_no_id, query, [identifier])
    result_doc = _score(chunk_doc_title, doc_with_id_title, query, [identifier])

    assert result_content.total_score > result_section.total_score, (
        f"content ({result_content.total_score:.2f}) > section ({result_section.total_score:.2f})"
    )
    assert result_section.total_score > result_doc.total_score, (
        f"section ({result_section.total_score:.2f}) > doc-title ({result_doc.total_score:.2f})"
    )
