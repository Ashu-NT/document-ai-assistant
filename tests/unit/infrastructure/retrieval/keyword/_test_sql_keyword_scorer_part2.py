"""Unit tests for SqlKeywordScorer source-weighted and normalised scoring."""

from datetime import datetime, timezone

import pytest

from src.domain.common import ChunkType, DocumentType

from src.domain.retrieval import RetrievalQuery

from src.infrastructure.db.orm_models import ChunkORM, DocumentORM

from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import extract_query_terms

from src.infrastructure.retrieval.keyword.sql_keyword_scorer import SqlKeywordScorer

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
        created_at=datetime.now(timezone.utc),
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
        created_at=datetime.now(timezone.utc),
    )

def _score(
    chunk: ChunkORM,
    document: DocumentORM,
    query_text: str,
    identifiers: list[str] | None = None,
    chunk_types: list[ChunkType] | None = None,
):
    scorer = SqlKeywordScorer()
    query = RetrievalQuery(
        query_id="q_test",
        query_text=query_text,
        detected_identifiers=identifiers or [],
        chunk_types=chunk_types or [],
    )
    terms = extract_query_terms(query_text)
    return scorer.score(
        row=chunk,
        document=document,
        retrieval_query=query,
        query_text=query_text,
        query_terms=terms,
    )

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

def test_primary_type_fit_boosts_primary_chunk_type() -> None:
    """When chunk_types are ordered by preference, the chunk whose type matches
    chunk_types[0] (primary) must score exactly 3.0 more than an otherwise
    identical chunk whose type matches chunk_types[1] (secondary)."""
    doc = _make_document(title="Pump Manual", file_name="pump.pdf")

    # TROUBLESHOOTING intent preference order: [TROUBLESHOOTING, OPERATION_INSTRUCTION, ...]
    preferred_types = [
        ChunkType.TROUBLESHOOTING,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.GENERAL,
    ]
    shared_content = "Pump seal failure: replace the shaft seal."

    chunk_primary = _make_chunk(
        chunk_id="c_primary",
        content=shared_content,
        chunk_type=ChunkType.TROUBLESHOOTING,
        section_path='["7 Components", "Troubleshooting 7.4.5"]',
    )
    chunk_secondary = _make_chunk(
        chunk_id="c_secondary",
        content=shared_content,
        chunk_type=ChunkType.OPERATION_INSTRUCTION,
        section_path='["7 Components", "Troubleshooting 7.4.5"]',
    )

    result_primary = _score(chunk_primary, doc, "pump seal failure remedies", chunk_types=preferred_types)
    result_secondary = _score(chunk_secondary, doc, "pump seal failure remedies", chunk_types=preferred_types)

    assert result_primary.metadata["sql_primary_type_fit"] == "true"
    assert result_secondary.metadata["sql_primary_type_fit"] == "false"
    assert result_primary.total_score == pytest.approx(result_secondary.total_score + 3.0)

def test_non_primary_type_still_gets_chunk_type_fit_bonus() -> None:
    """A chunk whose type is in chunk_types but not position 0 still gets the
    base chunk_type_fit bonus (+6.0), just not the primary bonus (+3.0)."""
    doc = _make_document(title="Manual", file_name="manual.pdf")
    preferred_types = [
        ChunkType.TROUBLESHOOTING,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.GENERAL,
    ]
    chunk_secondary = _make_chunk(
        content="Operation steps for the pump.",
        chunk_type=ChunkType.OPERATION_INSTRUCTION,
    )
    chunk_no_fit = _make_chunk(
        chunk_id="c_no_fit",
        content="Operation steps for the pump.",
        chunk_type=ChunkType.INSTALLATION_INSTRUCTION,
    )

    result_secondary = _score(chunk_secondary, doc, "pump operation", chunk_types=preferred_types)
    result_no_fit = _score(chunk_no_fit, doc, "pump operation", chunk_types=preferred_types)

    assert result_secondary.total_score == pytest.approx(result_no_fit.total_score + 6.0)

def test_section_path_requires_two_term_hits_for_any_depth() -> None:
    """Both shallow and deep section paths require at least 2 query-term
    hits in the local part to trigger the local_section_match bonus."""
    doc = _make_document(title="Pump Manual", file_name="pump.pdf")

    # 2-segment path with only 1 query-term match — no bonus
    chunk_shallow = _make_chunk(
        content="Press the green start button to run the macerator.",
        section_path='["6 Operation & General Maintenance", "6.3 Operation Macerator"]',
    )
    result_shallow = _score(chunk_shallow, doc, "How do I start and run the macerator?")
    assert result_shallow.metadata["sql_local_section_match"] == "false", (
        "2-part section with only 1 matching term should not get local_section_match"
    )

    # 3-segment path: 'macerator' does not match 'Macerators' as a whole word — 0 hits
    chunk_deep = _make_chunk(
        chunk_id="c_deep",
        content="Press the green button.",
        section_path='["7 Components", "7.1 Macerators", "General Overview"]',
    )
    result_deep = _score(chunk_deep, doc, "How do I start and run the macerator?")
    assert result_deep.metadata["sql_local_section_match"] == "false"

def test_section_term_match_requires_whole_word_not_substring() -> None:
    """A query term must appear as a whole word in the section path, not as a
    substring of a longer token: 'do' must not fire on 'shutdown'."""
    doc = _make_document(title="Manual", file_name="manual.pdf")

    # Section includes 'shutdown' (contains 'do') and 'Initial Test Run' (contains 'run').
    # With substring matching: 'do' in 'shutdown' + 'run' in 'Initial Test Run' = 2 hits = threshold.
    # With whole-word matching: only 'run' is a standalone word = 1 hit < threshold → no match.
    chunk = _make_chunk(
        content="Ensure covers are fitted before starting the machine.",
        section_path='["7 Components", "7.1 Macerators", "Commissioning & Shutdown", "7.2.7.2 Initial Test Run"]',
    )
    result = _score(chunk, doc, "How do I start and run the macerator?")
    assert result.metadata["sql_local_section_match"] == "false", (
        "'do' must not match as substring of 'shutdown' — whole-word required"
    )

def test_document_scope_identifier_gets_reduced_content_boost() -> None:
    """When the query identifier appears in the document title/filename, content matches
    receive a reduced boost compared to an evidence identifier (not in document name)."""
    # Doc A: FWC12 IS in the title → FWC12 is a document-scope identifier for its chunks
    doc_a = _make_document(
        doc_id="doc_fwc12",
        title="FWC12 Macerator Operating Manual",
        file_name="FWC12_manual.pdf",
    )
    # Doc B: FWC12 NOT in title → FWC12 is an evidence identifier for its chunks
    doc_b = _make_document(
        doc_id="doc_other",
        title="Marine Equipment Reference",
        file_name="marine_ref.pdf",
    )

    # Both chunks have identical content mentioning FWC12
    shared_content = "The FWC12 macerator spare parts are listed in the table below."
    chunk_docscope = _make_chunk(
        chunk_id="c_docscope",
        document_id="doc_fwc12",
        content=shared_content,
    )
    chunk_evidence = _make_chunk(
        chunk_id="c_evidence",
        document_id="doc_other",
        content=shared_content,
    )

    result_docscope = _score(chunk_docscope, doc_a, "FWC12 spare parts", ["FWC12"])
    result_evidence = _score(chunk_evidence, doc_b, "FWC12 spare parts", ["FWC12"])

    # Evidence identifier in content must score substantially higher
    assert result_evidence.total_score > result_docscope.total_score, (
        f"evidence ({result_evidence.total_score:.2f}) should beat "
        f"doc-scope ({result_docscope.total_score:.2f})"
    )
    # The gap must be significant (22 vs 4 per match + 6 vs 1 bonus = 18-pt gap)
    assert result_evidence.total_score - result_docscope.total_score > 15

    # Metadata: both report content_identifier_matches=1
    assert result_docscope.metadata["sql_content_identifier_matches"] == "1"
    assert result_evidence.metadata["sql_content_identifier_matches"] == "1"
    # But their doc-scope classification differs
    assert result_docscope.metadata["sql_content_docscope_matches"] == "1"
    assert result_docscope.metadata["sql_content_evidence_matches"] == "0"
    assert result_evidence.metadata["sql_content_evidence_matches"] == "1"
    assert result_evidence.metadata["sql_content_docscope_matches"] == "0"
