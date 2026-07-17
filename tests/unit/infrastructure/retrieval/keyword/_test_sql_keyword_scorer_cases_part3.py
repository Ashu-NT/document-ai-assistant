from tests.unit.infrastructure.retrieval.keyword._test_sql_keyword_scorer_support import *  # noqa: F401,F403

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
    from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
        section_path_hit,
    )
    from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import normalize_query_text

    normalized = normalize_query_text(section_path_variant)
    padded = f" {normalized} "
    result = section_path_hit(query_term, padded)
    assert result == should_match, (
        f"section_path_hit('{query_term}', '...{section_path_variant}...') "
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
