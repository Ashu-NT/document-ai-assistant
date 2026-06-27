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


# ---------------------------------------------------------------------------
# 7. Primary-type-fit bonus: most-preferred type gets +3 over secondary types
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 8. Shallow section path: single matching term triggers section bonus
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 9. Section term matching is whole-word — substrings in longer tokens don't match
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# G1 — Document-scope identifier dampening
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# G2 — Morphological section-path matching
# ---------------------------------------------------------------------------

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


@pytest.mark.parametrize(
    ("query_term", "section_path_variant", "should_match"),
    [
        # electrical family
        ("electrically", "Electrical Connection", True),
        ("electrical", "Electrically Connected Device", True),
        # connect family
        ("connected", "Connecting the Device", True),
        ("connection", "Connected terminals", True),
        ("connecting", "Connection diagram", True),
        # calibration family
        ("calibrated", "Calibration procedure", True),
        ("calibration", "Calibrated output", True),
        # lubrication family
        ("lubrication", "Lubricating the seal", True),
        ("lubricating", "Lubrication intervals", True),
        # install family
        ("installing", "Installation notes", True),
        ("installation", "Installing the device", True),
        # no cross-family matching
        ("electrical", "Installation guide", False),
        ("connected", "Calibration procedure", False),
    ],
)
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


# ---------------------------------------------------------------------------
# G2 extended — new morphological families (singular/plural, verb stems,
# British/American spelling)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("query_term", "section_path_variant", "should_match"),
    [
        # macerator/macerators
        ("macerator", "7.1 Macerators", True),
        ("macerators", "Macerator Maintenance", True),
        # quantity/quantities
        ("quantity", "Oil Quantities & Specification", True),
        ("quantities", "Oil Quantity and Grade", True),
        # remove/removal
        ("removed", "Removal of the Screen Basket", True),
        ("removal", "Removing the Cover", True),
        ("remove", "Removal Instructions", True),
        # optimize/optimise variants
        ("optimize", "Setting & Optimising the Press Discharge", True),
        ("optimising", "Optimize Discharge Pressure", True),
        ("optimised", "Optimizing the Output", True),
        # pump/pumps
        ("pump", "Transfer Pumps Overview", True),
        ("pumps", "Pump Maintenance", True),
        # interval/intervals
        ("interval", "Maintenance Intervals", True),
        ("intervals", "Inspection Interval Schedule", True),
        # operate/operation
        ("operation", "Operating Procedure", True),
        ("operating", "Operation Manual", True),
        # No false cross-family matches
        ("macerator", "Food Waste Press Overview", False),
        ("removal", "Maintenance Schedule", False),
    ],
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


# ---------------------------------------------------------------------------
# G1 (redesigned) — Ancestor section path tiebreaker
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# expand_query_terms_with_morph_variants — SQL ILIKE candidate widening
# ---------------------------------------------------------------------------

def test_expand_query_terms_includes_morph_variants() -> None:
    """expand_query_terms_with_morph_variants must return original terms plus
    all morphological variants not already present."""
    from src.infrastructure.retrieval.keyword.sql_keyword_scorer import (
        expand_query_terms_with_morph_variants,
    )

    expanded = expand_query_terms_with_morph_variants(["removed"])
    assert "removed" in expanded
    assert "removal" in expanded
    assert "remove" in expanded
    assert "removing" in expanded


def test_expand_query_terms_no_duplicates() -> None:
    """When a variant is also an original term, it must not appear twice."""
    from src.infrastructure.retrieval.keyword.sql_keyword_scorer import (
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
    from src.infrastructure.retrieval.keyword.sql_keyword_scorer import (
        expand_query_terms_with_morph_variants,
    )

    expanded = expand_query_terms_with_morph_variants(["xyzunknownterm"])
    assert expanded == ["xyzunknownterm"]


def test_expand_query_terms_covers_optimize_family() -> None:
    """Query term 'optimize' expands to include British spelling 'optimising',
    fixing M-013 where the section title uses British spelling."""
    from src.infrastructure.retrieval.keyword.sql_keyword_scorer import (
        expand_query_terms_with_morph_variants,
    )

    expanded = expand_query_terms_with_morph_variants(["optimize"])
    assert "optimising" in expanded, "'optimising' must be in expansion of 'optimize'"
    assert "optimise" in expanded
    assert "optimised" in expanded
    assert "optimized" in expanded


def test_expand_query_terms_preserves_original_term_order() -> None:
    """Original terms appear first in the returned list, followed by new variants."""
    from src.infrastructure.retrieval.keyword.sql_keyword_scorer import (
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
