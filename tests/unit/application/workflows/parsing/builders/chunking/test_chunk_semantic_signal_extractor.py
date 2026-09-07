from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_semantic_signal_extractor import (
    ChunkSemanticSignalExtractor,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.domain.common import ChunkType


def make_extractor() -> ChunkSemanticSignalExtractor:
    return ChunkSemanticSignalExtractor()


def test_title_marker_hit_scores_four_points() -> None:
    extractor = make_extractor()

    scores = extractor.extract(section_title="Troubleshooting", section_path=[], text="")

    assert scores == {ChunkType.TROUBLESHOOTING: 4}


def test_local_section_path_marker_hit_scores_three_points() -> None:
    # A path with 1-2 segments counts entirely as "local" (see
    # _path_texts) -- title is separate from path, so this isolates the
    # local-path weight (x3) from the title weight (x4).
    extractor = make_extractor()

    scores = extractor.extract(
        section_title=None, section_path=["Troubleshooting"], text=""
    )

    assert scores == {ChunkType.TROUBLESHOOTING: 3}


def test_title_and_local_path_hits_combine() -> None:
    extractor = make_extractor()

    scores = extractor.extract(
        section_title="Troubleshooting", section_path=["Troubleshooting"], text=""
    )

    assert scores == {ChunkType.TROUBLESHOOTING: 7}


def test_ancestor_path_marker_hits_score_at_face_value_for_non_safety_types() -> None:
    # A path with 3+ segments splits into local (last two) and ancestor
    # (everything before). "Problem Error Log" as the sole ancestor
    # segment hits two distinct TROUBLESHOOTING markers ("problem",
    # "error"); for any type other than SAFETY_WARNING, the ancestor bonus
    # is the raw hit count, unweighted.
    extractor = make_extractor()

    scores = extractor.extract(
        section_title=None,
        section_path=["Problem Error Log", "Sub A", "Sub B"],
        text="",
    )

    assert scores == {ChunkType.TROUBLESHOOTING: 2}


def test_safety_warning_ancestor_only_hits_are_capped_at_one() -> None:
    # Same shape as above, but for SAFETY_WARNING specifically: when the
    # only evidence is an ancestor-level mention (no title, no local-path
    # hit), _ancestor_path_bonus caps the contribution at 1 regardless of
    # how many safety markers appear in the ancestor segment -- a distant
    # "Safety" ancestor is weak evidence and must not score as strongly as
    # a real safety-titled section.
    extractor = make_extractor()

    scores = extractor.extract(
        section_title=None,
        section_path=["Safety Warnings", "Sub A", "Sub B"],
        text="",
    )

    assert scores == {ChunkType.SAFETY_WARNING: 1}


def test_content_marker_score_is_capped_at_two_by_default() -> None:
    # MAINTENANCE_PROCEDURE has no entry in CONTENT_SCORE_CAPS, so its
    # default cap is 2 even though the text hits six distinct markers.
    extractor = make_extractor()
    text = (
        "Remove the old filter, replace it, inspect the seal, tighten the "
        "bolts, verify operation, then reinstall the cover."
    )

    scores = extractor.extract(section_title=None, section_path=[], text=text)

    assert scores == {ChunkType.MAINTENANCE_PROCEDURE: 2}


def test_content_marker_score_respects_a_higher_configured_cap() -> None:
    # TECHNICAL_SPECIFICATION has an explicit cap of 4 in CONTENT_SCORE_CAPS
    # -- five distinct marker hits still cap at 4, not the default 2.
    extractor = make_extractor()
    text = (
        "Serial number and model number are printed on the label. See "
        "part number and drawing number below. The order code follows."
    )

    scores = extractor.extract(section_title=None, section_path=[], text=text)

    assert scores == {ChunkType.TECHNICAL_SPECIFICATION: 4}


def test_interval_pattern_adds_a_flat_four_point_bonus() -> None:
    extractor = make_extractor()

    scores = extractor.extract(
        section_title=None, section_path=[], text="Perform this every 6 months."
    )

    assert scores == {ChunkType.MAINTENANCE_INTERVAL: 4}


def test_spec_value_pattern_adds_a_flat_two_point_bonus() -> None:
    extractor = make_extractor()

    scores = extractor.extract(
        section_title=None, section_path=[], text="The output is rated at 24 V."
    )

    assert scores == {ChunkType.TECHNICAL_SPECIFICATION: 2}


def test_table_ids_alone_add_a_flat_technical_specification_bonus() -> None:
    # Presence of any table_ids adds +1 to TECHNICAL_SPECIFICATION on its
    # own, even when the content has no table-shaped marker evidence at
    # all -- a table is itself weak evidence of "spec-like" content.
    extractor = make_extractor()

    scores = extractor.extract(
        section_title=None,
        section_path=[],
        text="Nothing special here at all today.",
        table_ids=["t1"],
    )

    assert scores == {ChunkType.TECHNICAL_SPECIFICATION: 1}


def test_table_ids_with_strong_table_marker_evidence_triggers_direct_table_bias() -> (
    None
):
    # Content whose table-shaped markers clear MAINTENANCE_INTERVAL's
    # threshold (2) triggers ChunkTableSignalScorer's direct-table-evidence
    # bias: a further +5 on top of the table score, layered on top of the
    # regular content-marker score ("frequency" also matches the ordinary
    # CONTENT_MARKERS list for MAINTENANCE_INTERVAL).
    extractor = make_extractor()

    scores = extractor.extract(
        section_title=None,
        section_path=[],
        text="task interval frequency",
        table_ids=["t1"],
    )

    assert scores == {
        ChunkType.MAINTENANCE_INTERVAL: 10,
        ChunkType.TECHNICAL_SPECIFICATION: 1,
    }


def test_extract_from_fragment_delegates_using_the_fragments_own_metadata() -> None:
    extractor = make_extractor()
    fragment = ChunkFragment(
        text="Check the fuse and inspect the relay.",
        chunk_type=ChunkType.GENERAL,
        section_title="Troubleshooting",
        section_path=["Troubleshooting"],
    )

    scores = extractor.extract_from_fragment(fragment)

    assert scores == {
        ChunkType.TROUBLESHOOTING: 7,
        ChunkType.MAINTENANCE_PROCEDURE: 1,
    }


def test_extract_from_fragments_uses_only_the_first_fragments_title_and_path() -> None:
    # Documented, deliberate behavior (see the comment in
    # extract_from_fragments): section metadata describes the final merged
    # chunk, not every input fragment, so only fragments[0]'s section_title/
    # section_path contribute title/path scoring -- content from every
    # fragment is still combined. Swapping fragment order changes which
    # type's title/path score applies, while the shared content-marker
    # contribution (MAINTENANCE_PROCEDURE: 1, from "inspect") stays put.
    extractor = make_extractor()
    troubleshooting_fragment = ChunkFragment(
        text="Check the fuse and inspect the relay.",
        chunk_type=ChunkType.GENERAL,
        section_title="Troubleshooting",
        section_path=["Troubleshooting"],
    )
    certification_fragment = ChunkFragment(
        text="This part is unrelated content with a certificate marker.",
        chunk_type=ChunkType.GENERAL,
        section_title="Certification",
        section_path=["Certification"],
    )

    troubleshooting_first = extractor.extract_from_fragments(
        [troubleshooting_fragment, certification_fragment]
    )
    certification_first = extractor.extract_from_fragments(
        [certification_fragment, troubleshooting_fragment]
    )

    assert troubleshooting_first == {
        ChunkType.TROUBLESHOOTING: 7,
        ChunkType.MAINTENANCE_PROCEDURE: 1,
    }
    assert certification_first == {
        ChunkType.CERTIFICATION_INFO: 7,
        ChunkType.MAINTENANCE_PROCEDURE: 1,
    }


def test_extract_from_fragments_honors_an_explicit_content_override() -> None:
    extractor = make_extractor()
    fragment = ChunkFragment(
        text="Check the fuse and inspect the relay.",
        chunk_type=ChunkType.GENERAL,
        section_title="Troubleshooting",
        section_path=["Troubleshooting"],
    )

    scores = extractor.extract_from_fragments(
        [fragment], content="troubleshooting override text"
    )

    assert scores == {ChunkType.TROUBLESHOOTING: 7}


def test_extract_from_fragments_dedups_table_ids_across_fragments() -> None:
    extractor = make_extractor()
    fragment_a = ChunkFragment(
        text="x", chunk_type=ChunkType.GENERAL, table_ids=["ta"]
    )
    fragment_b = ChunkFragment(
        text="y", chunk_type=ChunkType.GENERAL, table_ids=["tb", "ta"]
    )

    scores = extractor.extract_from_fragments(
        [fragment_a, fragment_b], content="plain text"
    )

    # A flat +1 regardless of table count confirms table_ids were deduped
    # into a set-like union, not summed per-occurrence.
    assert scores == {ChunkType.TECHNICAL_SPECIFICATION: 1}


def test_extract_from_fragments_returns_empty_for_no_fragments() -> None:
    extractor = make_extractor()

    assert extractor.extract_from_fragments([]) == {}
