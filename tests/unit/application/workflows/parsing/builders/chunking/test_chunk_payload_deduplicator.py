from src.application.workflows.parsing.builders.chunking.deduplication import (
    ChunkPayloadDeduplicator,
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
    chunk_type: ChunkType = ChunkType.GENERAL,
    table_ids: list[str] | None = None,
    page_start: int = 1,
    page_end: int = 1,
) -> ChunkPayload:
    return ChunkPayload(
        section_id=section_id,
        section_path=section_path or ["Section"],
        content=content,
        chunk_type=chunk_type,
        embedding_text=content,
        table_ids=table_ids or [],
        page_start=page_start,
        page_end=page_end,
    )


def test_exact_duplicate_payloads_collapse() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    payload = make_payload(content="Replace hydraulic filter every 1000 hours.")

    result = deduplicator.deduplicate([payload, make_payload(content=payload.content)])

    assert len(result.payloads) == 1
    assert result.diagnostics[0]["reason"] == "exact_normalized_content"


def test_context_only_duplicate_collapses_into_atomic_chunk() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    atomic_payload = make_payload(
        content="Replace hydraulic filter every 1000 hours."
    )
    context_payload = make_payload(
        content="Context: Replace hydraulic filter every 1000 hours."
    )

    result = deduplicator.deduplicate([context_payload, atomic_payload])

    assert len(result.payloads) == 1
    assert result.payloads[0].content == atomic_payload.content
    assert result.diagnostics[0]["reason"] == "context_companion_duplicate"


def test_section_overview_with_unique_summary_remains() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    atomic_payload = make_payload(
        content="Replace hydraulic filter every 1000 hours."
    )
    overview_payload = make_payload(
        content=(
            "Section overview: Replace hydraulic filter every 1000 hours.\n\n"
            "Subsections: filter removal; filter installation."
        ),
        chunk_type=ChunkType.OVERVIEW,
        section_path=["Maintenance"],
    )

    result = deduplicator.deduplicate([overview_payload, atomic_payload])

    assert len(result.payloads) == 2


def test_normal_overlapping_chunks_remain_when_unique_context_exists() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    shared_tokens = " ".join(f"shared{i}" for i in range(30))
    first_payload = make_payload(
        content=f"{shared_tokens} " + " ".join(f"left{i}" for i in range(25))
    )
    second_payload = make_payload(
        content=f"{shared_tokens} " + " ".join(f"right{i}" for i in range(25))
    )

    result = deduplicator.deduplicate([first_payload, second_payload])

    assert len(result.payloads) == 2


def test_different_table_rows_remain() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    first_row = make_payload(
        content="| Part | Description |\n| HP-001 | Filter |",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        table_ids=["table_001"],
    )
    second_row = make_payload(
        content="| Part | Description |\n| HP-002 | Seal |",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        table_ids=["table_001"],
    )

    result = deduplicator.deduplicate([first_row, second_row])

    assert len(result.payloads) == 2


def test_different_identifiers_remain() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    first_payload = make_payload(
        content="Approval BG: ATEX II 3 G Ex ic IIC T6...T4 Gc."
    )
    second_payload = make_payload(
        content="Approval IE: IECEx Ex ic IIC T6...T4 Gc."
    )

    result = deduplicator.deduplicate([first_payload, second_payload])

    assert len(result.payloads) == 2


def test_different_structured_item_labels_remain() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    broader_payload = make_payload(
        content=(
            "15 - COMBINED\n"
            "ANCHOR / MASTHEAD LANTERN WHITE / WHITE\n"
            "3540.6000\n"
            "16 - COMBINED\n"
            "ANCHOR/ TOWING LANTERN WHITE / YELLOW\n"
            "3540.7000"
        ),
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Lamp labels"],
    )
    narrower_payload = make_payload(
        content=(
            "ANCHOR / MASTHEAD LANTERN WHITE / WHITE\n"
            "3540.6000\n"
            "16 - COMBINED\n"
            "ANCHOR/ TOWING LANTERN WHITE / YELLOW\n"
            "3540.7000"
        ),
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Lamp labels"],
    )

    result = deduplicator.deduplicate([broader_payload, narrower_payload])

    assert len(result.payloads) == 2


def test_structured_evidence_wins_over_overview_duplicate() -> None:
    deduplicator = ChunkPayloadDeduplicator()
    overview_payload = make_payload(
        content=(
            "Section overview: PMC51 PMP5x BG ATEX II 3 G Ex ic IIC T6 T4 Gc "
            "IE IECEx Ex ic IIC T6 T4 Gc"
        ),
        chunk_type=ChunkType.OVERVIEW,
        section_path=["Basic specifications"],
    )
    structured_payload = make_payload(
        content="PMC51 PMP5x BG ATEX II 3 G Ex ic IIC T6 T4 Gc IE IECEx Ex ic IIC T6 T4 Gc",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        table_ids=["table_approval"],
        section_path=["Safety Instructions", "Extended order code: Cerabar M"],
    )

    result = deduplicator.deduplicate([overview_payload, structured_payload])

    assert len(result.payloads) == 1
    assert result.payloads[0].chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert result.diagnostics[0]["reason"] == "overview_duplicate"
