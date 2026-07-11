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

def test_document_scope_identifier_section_match_also_dampened() -> None:
    """Section-path match for a document-scope identifier is also dampened vs evidence."""
    doc_fwc12 = _make_document(
        doc_id="doc_fwc12",
        title="FWC12 Macerator Manual",
        file_name="FWC12_manual.pdf",
    )
    doc_generic = _make_document(
        doc_id="doc_gen",
        title="Generic Pump Manual",
        file_name="pump_manual.pdf",
    )

    # Section path carries FWC12 — doc-scope vs evidence
    chunk_docscope_section = _make_chunk(
        chunk_id="c_ds_section",
        document_id="doc_fwc12",
        content="Oil change intervals are described in this section.",
        section_path='["9 Maintenance", "9.1 FWC12 Maintenance Intervals"]',
    )
    chunk_evidence_section = _make_chunk(
        chunk_id="c_ev_section",
        document_id="doc_gen",
        content="Oil change intervals are described in this section.",
        section_path='["9 Maintenance", "9.1 FWC12 Maintenance Intervals"]',
    )

    result_docscope = _score(
        chunk_docscope_section, doc_fwc12, "FWC12 maintenance interval", ["FWC12"]
    )
    result_evidence = _score(
        chunk_evidence_section, doc_generic, "FWC12 maintenance interval", ["FWC12"]
    )

    assert result_evidence.total_score > result_docscope.total_score, (
        "Evidence section identifier must outscore document-scope section identifier"
    )

def test_document_scope_identifier_content_still_beats_document_only() -> None:
    """Even a dampened doc-scope content match still beats a document-title-only match."""
    doc = _make_document(
        doc_id="doc_fwc12",
        title="FWC12 Macerator Manual",
        file_name="FWC12_manual.pdf",
    )

    chunk_content = _make_chunk(
        chunk_id="c_content",
        document_id="doc_fwc12",
        content="The FWC12 oil fill point is located on the port side.",
    )
    chunk_doc_only = _make_chunk(
        chunk_id="c_doc_only",
        document_id="doc_fwc12",
        content="This section describes general safety procedures.",
        section_path='["1 Safety"]',
    )

    result_content = _score(chunk_content, doc, "FWC12 oil fill", ["FWC12"])
    result_doc_only = _score(chunk_doc_only, doc, "FWC12 oil fill", ["FWC12"])

    assert result_content.total_score > result_doc_only.total_score, (
        "Doc-scope content match (4+1=5 pts) must still beat doc-only match (2 pts)"
    )

def test_section_path_matches_inflected_query_term_electrically_connected() -> None:
    """'electrically'/'connected' in a query must match 'electrical'/'connection' in
    a section path via morphological normalization."""
    doc = _make_document(title="Pressure Transmitter Manual", file_name="transmitter.pdf")

    chunk_morpho = _make_chunk(
        content="Connect terminals 1+ and 2- to the 24 V DC supply. Terminal 3 to earth.",
        section_path='["5 Electrical Connection", "5.1 Connecting the Device"]',
    )
    chunk_unrelated = _make_chunk(
        chunk_id="c_unrelated",
        content="Connect terminals 1+ and 2- to the 24 V DC supply. Terminal 3 to earth.",
        section_path='["5 Installation", "5.1 Mounting the Device"]',
    )

    query_text = "How should the device be electrically connected?"
    result_morpho = _score(chunk_morpho, doc, query_text)
    result_unrelated = _score(chunk_unrelated, doc, query_text)

    assert result_morpho.metadata["sql_local_section_match"] == "true", (
        "'electrically' and 'connected' should match 'electrical' and 'connection'/'connecting' "
        "in section path via morphological normalization"
    )
    assert result_unrelated.metadata["sql_local_section_match"] == "false"
    assert result_morpho.total_score > result_unrelated.total_score

def test_morphological_section_path_hit_variants(
    query_term: str,
    section_path_variant: str,
    should_match: bool,
) -> None:
    """Morphological variant matching is applied specifically to section-path lookup."""
    from src.infrastructure.retrieval.keyword.sql_keyword_scorer import (
        _section_path_hit,
        _MORPH_VARIANTS,
    )
    from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import (
        normalize_query_text,
    )

    normalized = normalize_query_text(section_path_variant)
    padded = f" {normalized} "
    result = _section_path_hit(query_term, padded)
    assert result == should_match, (
        f"_section_path_hit('{query_term}', '...{section_path_variant}...') "
        f"expected {should_match}, got {result}"
    )

def test_extended_morphological_section_path_hit_variants(
    query_term: str,
    section_path_variant: str,
    should_match: bool,
) -> None:
    """Extended morph families cover singular/plural, verbal nouns, and British spellings."""
    from src.infrastructure.retrieval.keyword.sql_keyword_scorer import _section_path_hit
    from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import normalize_query_text

    normalized = normalize_query_text(section_path_variant)
    padded = f" {normalized} "
    result = _section_path_hit(query_term, padded)
    assert result == should_match, (
        f"_section_path_hit('{query_term}', '...{section_path_variant}...') "
        f"expected {should_match}, got {result}"
    )

def test_ancestor_tiebreaker_disambiguates_sibling_sections() -> None:
    """When two chunks both have local_section_match=True, query terms present in
    the ancestor path grant a small specificity bonus — letting the chunk from
    the correct sub-system outscore its sibling even when their local paths
    are otherwise equivalent.

    Both chunks are given identical content so that term-match and ordered-match
    scores are equal and the only scoring difference comes from the ancestor path.
    """
    doc = _make_document(title="FWC12 System Manual", file_name="fwc12_manual.pdf")

    # Shared content — deliberately identical so content scores cancel out.
    shared_content = (
        "Maintenance intervals: first maintenance after 1 month, then annually. "
        "Check wear parts at each maintenance intervals inspection."
    )

    # Expected chunk: ancestor "7.1 Macerators" carries the query term "macerator".
    chunk_expected = _make_chunk(
        chunk_id="c_expected",
        content=shared_content,
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path='["7 Components", "7.1 Macerators", "Maintenance", "Maintenance Intervals"]',
    )
    # Competing chunk: ancestor "7.2 Food Waste Press" does NOT contain "macerator".
    chunk_sibling = _make_chunk(
        chunk_id="c_sibling",
        content=shared_content,
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path='["7 Components", "7.2 Food Waste Press", "Overview & Maintenance Intervals"]',
    )

    query_text = "What are the maintenance intervals for the macerator?"
    result_expected = _score(chunk_expected, doc, query_text)
    result_sibling = _score(chunk_sibling, doc, query_text)

    assert result_expected.metadata["sql_local_section_match"] == "true"
    assert result_sibling.metadata["sql_local_section_match"] == "true"
    assert result_expected.total_score > result_sibling.total_score, (
        f"Macerator section ({result_expected.total_score:.2f}) should outscore "
        f"Food Waste Press section ({result_sibling.total_score:.2f}) "
        f"via ancestor tiebreaker on 'macerator' → 'macerators'"
    )
