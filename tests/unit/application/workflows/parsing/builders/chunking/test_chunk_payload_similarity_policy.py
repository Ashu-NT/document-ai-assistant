from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_signature import (
    ChunkPayloadSignature,
)
from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_similarity_policy import (
    ChunkPayloadSimilarityPolicy,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.domain.common import ChunkType


def make_payload(
    *,
    content: str,
    section_id: str = "sec_001",
    section_path: list[str] | None = None,
    section_ids: list[str] | None = None,
    chunk_type: ChunkType = ChunkType.GENERAL,
    table_ids: list[str] | None = None,
    page_start: int | None = 1,
    page_end: int | None = 1,
) -> ChunkPayload:
    return ChunkPayload(
        section_id=section_id,
        section_path=section_path or ["Section"],
        content=content,
        chunk_type=chunk_type,
        embedding_text=content,
        section_ids=section_ids or [],
        table_ids=table_ids or [],
        page_start=page_start,
        page_end=page_end,
    )


def duplicate_reason(left: ChunkPayload, right: ChunkPayload) -> str | None:
    policy = ChunkPayloadSimilarityPolicy()
    return policy.duplicate_reason(
        left_payload=left,
        left_signature=ChunkPayloadSignature.from_payload(left),
        right_payload=right,
        right_signature=ChunkPayloadSignature.from_payload(right),
    )


def test_exact_duplicate_content_in_the_same_section_is_flagged() -> None:
    left = make_payload(content="Replace hydraulic filter every 1000 hours.")
    right = make_payload(content="Replace hydraulic filter every 1000 hours.")

    assert duplicate_reason(left, right) == "exact_normalized_content"


def test_identical_content_in_unrelated_sections_is_not_flagged() -> None:
    # _paths_or_pages_related gates everything else -- two payloads with no
    # shared section_id/section_ids/path/page overlap must never be
    # compared at all, even when their content is byte-identical.
    left = make_payload(
        content="Replace hydraulic filter every 1000 hours.",
        section_id="sec_a",
        section_path=["Maintenance"],
        page_start=1,
        page_end=1,
    )
    right = make_payload(
        content="Replace hydraulic filter every 1000 hours.",
        section_id="sec_b",
        section_path=["Unrelated Chapter"],
        page_start=50,
        page_end=50,
    )

    assert duplicate_reason(left, right) is None


def test_context_companion_duplicate_collapses_into_atomic_content() -> None:
    atomic = make_payload(content="Replace hydraulic filter every 1000 hours.")
    context_companion = make_payload(
        content="Context: Replace hydraulic filter every 1000 hours."
    )

    assert duplicate_reason(atomic, context_companion) == "context_companion_duplicate"


def test_overview_with_comparable_body_matching_atomic_content_is_flagged() -> None:
    # Regression for the dead-gate bug fixed earlier this session: an
    # overview chunk whose own title/body genuinely duplicates a real
    # content chunk must be caught, not exempted just for having a
    # subsections listing.
    atomic = make_payload(content="Replace hydraulic filter every 1000 hours.")
    overview = make_payload(
        content=(
            "Section overview: Replace hydraulic filter every 1000 hours.\n\n"
            "Direct subsections (2): filter removal; filter installation."
        ),
        chunk_type=ChunkType.OVERVIEW,
    )

    assert duplicate_reason(atomic, overview) == "overview_duplicate"


def test_overview_with_no_comparable_body_is_never_flagged() -> None:
    # When the overview has no title and nothing but the subsections
    # listing, has_comparable_overview_body is False -- overview_body_content
    # drops the whole "direct subsections" line, leaving nothing to compare.
    atomic = make_payload(content="Replace hydraulic filter every 1000 hours.")
    overview = make_payload(
        content="Direct subsections (2): filter removal; filter installation.",
        chunk_type=ChunkType.OVERVIEW,
    )

    assert duplicate_reason(atomic, overview) is None


def test_overview_with_unrelated_comparable_body_is_not_flagged() -> None:
    # Has a comparable body (its own title), but that body shares nothing
    # with the atomic chunk's content -- must not collapse.
    atomic = make_payload(content="Replace hydraulic filter every 1000 hours.")
    overview = make_payload(
        content=(
            "Section overview: Electrical Safety\n\n"
            "Direct subsections (2): grounding; lockout tagout."
        ),
        chunk_type=ChunkType.OVERVIEW,
    )

    assert duplicate_reason(atomic, overview) is None


def test_shared_touched_section_id_makes_otherwise_unrelated_payloads_comparable() -> (
    None
):
    # Regression for the section_ids fix: a merged chunk's primary
    # section_id/section_path may collapse to a common ancestor, but its
    # section_ids lists every subsection it actually touched. Two payloads
    # whose *primary* sections differ must still be compared if they share
    # a touched section id.
    left = make_payload(
        content="Replace hydraulic filter every 1000 hours.",
        section_id="sec_ancestor",
        section_path=["1 General"],
        section_ids=["sec_ancestor", "sec_17", "sec_18"],
        page_start=None,
        page_end=None,
    )
    right = make_payload(
        content="Replace hydraulic filter every 1000 hours.",
        section_id="sec_18",
        section_path=["1 General", "1.8 Liability and Warranty"],
        section_ids=["sec_18"],
        page_start=None,
        page_end=None,
    )

    assert duplicate_reason(left, right) == "exact_normalized_content"


def test_high_containment_near_duplicate_atomic_chunks_are_flagged() -> None:
    shared_tokens = " ".join(f"word{i}" for i in range(30))
    left = make_payload(content=shared_tokens)
    right = make_payload(content=f"{shared_tokens} extra")

    assert duplicate_reason(left, right) == "high_containment_duplicate"


def test_overlapping_but_sufficiently_unique_chunks_are_not_flagged() -> None:
    shared_tokens = " ".join(f"shared{i}" for i in range(30))
    left = make_payload(content=f"{shared_tokens} " + " ".join(f"left{i}" for i in range(25)))
    right = make_payload(content=f"{shared_tokens} " + " ".join(f"right{i}" for i in range(25)))

    assert duplicate_reason(left, right) is None


def test_conflicting_identifiers_block_duplicate_detection() -> None:
    left = make_payload(content="Approval BG: ATEX II 3 G Ex ic IIC T6...T4 Gc.")
    right = make_payload(content="Approval IE: IECEx Ex ic IIC T6...T4 Gc.")

    assert duplicate_reason(left, right) is None


def test_different_table_rows_are_not_flagged_even_when_related() -> None:
    left = make_payload(
        content="| Part | Description |\n| HP-001 | Filter |",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        table_ids=["table_001"],
    )
    right = make_payload(
        content="| Part | Description |\n| HP-002 | Seal |",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        table_ids=["table_001"],
    )

    assert duplicate_reason(left, right) is None
