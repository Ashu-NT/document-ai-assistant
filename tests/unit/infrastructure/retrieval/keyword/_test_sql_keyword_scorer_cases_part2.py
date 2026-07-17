from tests.unit.infrastructure.retrieval.keyword._test_sql_keyword_scorer_support import *  # noqa: F401,F403

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
    from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
        MORPH_VARIANTS,
        section_path_hit,
    )
    from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import (
        normalize_query_text,
    )

    normalized = normalize_query_text(section_path_variant)
    padded = f" {normalized} "
    result = section_path_hit(query_term, padded)
    assert result == should_match, (
        f"section_path_hit('{query_term}', '...{section_path_variant}...') "
        f"expected {should_match}, got {result}"
    )
