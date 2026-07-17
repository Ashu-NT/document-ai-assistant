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

def test_ancestor_tiebreaker_morph_match_for_removal_section() -> None:
    """Query term 'removed' matches 'Removal' in ancestor path via morph family,
    giving the correct chunk a score advantage over an unrelated section."""
    doc = _make_document(title="Food Waste Press Manual", file_name="fwc12_manual.pdf")

    # Expected: section with "Removal" in local path
    chunk_expected = _make_chunk(
        chunk_id="c_removal",
        content=(
            "Pull the screen basket straight out carefully to prevent jamming. "
            "After roughly half its length is pulled out, resistance reduces considerably."
        ),
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        section_path='["7 Components", "7.2 Food Waste Press", "Maintenance & Cleaning of the Screen Basket", "Removal of the Screen Basket"]',
    )
    # Unrelated competitor: mentions screen basket but not removal procedure
    chunk_unrelated = _make_chunk(
        chunk_id="c_unrelated",
        content=(
            "The screen basket is a cylindrical filter element. If the screen basket "
            "and the screw are removed, maintenance of the shaft seals can be performed."
        ),
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        section_path='["7 Components", "7.2 Food Waste Press", "7.2.13.1 Maintenance of the Shaft & Shaft Seals", "Loosening the Retaining Plate Screw"]',
    )

    query_text = "How is the screen basket removed from the food waste press?"
    result_expected = _score(chunk_expected, doc, query_text)
    result_unrelated = _score(chunk_unrelated, doc, query_text)

    assert result_expected.metadata["sql_local_section_match"] == "true", (
        "'removed' should match 'Removal' in local section path via morph family"
    )
    assert result_expected.total_score > result_unrelated.total_score

def test_ancestor_tiebreaker_quantity_section_path() -> None:
    """Query 'quantity' matches 'Quantities' in local section path via morph family,
    giving expected chunk local_section_match=True when the winning chunk lacks it."""
    doc = _make_document(title="Vacuum Pump Manual", file_name="pump_manual.pdf")

    # Expected: "Oil Quantities & Specification" in local path
    chunk_expected = _make_chunk(
        chunk_id="c_oil_qty",
        content=(
            "Oil quantity horizontal 0.6 L, vertical 0.91 L. "
            "First oil change after approx. 500 hours or 12 months, "
            "then after each 2000 hours or 12 months. "
            "Oil specification SAE 75W-90 API GL-4 or GL-5."
        ),
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path='["7 Components", "7.3 Vacuum Transfer Pump", "Maintenance", "Oil Quantities & Specification"]',
    )
    # Competitor: "Lubrication Schedule" — has lubrication info but no "Oil Quantities"
    chunk_lubrication = _make_chunk(
        chunk_id="c_lubrication",
        content=(
            "After every 350 hours of operation. Filling quantity with hand-lever grease gun "
            "should not exceed 2 to 3 strokes per grease nipple."
        ),
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path='["7 Components", "7.3 Vacuum Transfer Pump", "Lubrication Schedule"]',
    )

    query_text = "What oil quantity and oil change interval are specified for the rotary lobe pump?"
    result_expected = _score(chunk_expected, doc, query_text)
    result_lubrication = _score(chunk_lubrication, doc, query_text)

    assert result_expected.metadata["sql_local_section_match"] == "true", (
        "'quantity' should match 'Quantities' in local section path via morph family"
    )
    assert result_expected.total_score > result_lubrication.total_score, (
        f"Oil Quantities section ({result_expected.total_score:.2f}) should outscore "
        f"Lubrication Schedule ({result_lubrication.total_score:.2f})"
    )

def test_expand_query_terms_includes_morph_variants() -> None:
    """expand_query_terms_with_morph_variants must return original terms plus
    all morphological variants not already present."""
    from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
        expand_query_terms_with_morph_variants,
    )

    expanded = expand_query_terms_with_morph_variants(["removed"])
    assert "removed" in expanded
    assert "removal" in expanded
    assert "remove" in expanded
    assert "removing" in expanded

def test_expand_query_terms_no_duplicates() -> None:
    """When a variant is also an original term, it must not appear twice."""
    from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
        expand_query_terms_with_morph_variants,
    )

    expanded = expand_query_terms_with_morph_variants(["remove", "removed"])
    assert expanded.count("remove") == 1
    assert expanded.count("removed") == 1
    # All other family members still present exactly once
    for term in ("removal", "removing"):
        assert expanded.count(term) == 1, f"'{term}' should appear exactly once, got {expanded.count(term)}"

def test_expand_query_terms_unknown_term_returned_unchanged() -> None:
    """Terms with no morph family are returned unchanged."""
    from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
        expand_query_terms_with_morph_variants,
    )

    expanded = expand_query_terms_with_morph_variants(["xyzunknownterm"])
    assert expanded == ["xyzunknownterm"]

def test_expand_query_terms_covers_optimize_family() -> None:
    """Query term 'optimize' expands to include British spelling 'optimising',
    fixing M-013 where the section title uses British spelling."""
    from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
        expand_query_terms_with_morph_variants,
    )

    expanded = expand_query_terms_with_morph_variants(["optimize"])
    assert "optimising" in expanded, "'optimising' must be in expansion of 'optimize'"
    assert "optimise" in expanded
    assert "optimised" in expanded
    assert "optimized" in expanded

def test_expand_query_terms_preserves_original_term_order() -> None:
    """Original terms appear first in the returned list, followed by new variants."""
    from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
        expand_query_terms_with_morph_variants,
    )

    terms = ["removal", "pump"]
    expanded = expand_query_terms_with_morph_variants(terms)
    assert expanded[0] == "removal"
    assert expanded[1] == "pump"
    # Variants appear after originals
    for variant in ("remove", "removed", "removing"):
        assert variant in expanded
    assert "pumps" in expanded
