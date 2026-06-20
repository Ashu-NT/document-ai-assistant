import pytest

from src.application.workflows.parsing.builders.chunking.builders import (
    ChunkTypeResolver,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge_policy import (
    SectionMergePolicy,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ChunkType


def make_fragment(
    *,
    section_id: str = "sec_001",
    section_title: str,
    section_path: list[str] | None = None,
    text: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    parent_section_id: str | None = "sec_parent",
    token_count: int = 24,
    table_ids: list[str] | None = None,
) -> ChunkFragment:
    return ChunkFragment(
        text=text,
        chunk_type=chunk_type,
        section_id=section_id,
        section_title=section_title,
        section_path=section_path or ["Manual", section_title],
        section_level=2,
        parent_section_id=parent_section_id,
        token_count=token_count,
        table_ids=table_ids or [],
    )


@pytest.mark.parametrize(
    ("section_title", "text", "expected_chunk_type", "table_ids"),
    [
        (
            "Maintenance Procedure",
            "Remove the cover, inspect the seal, and reinstall the housing.",
            ChunkType.MAINTENANCE_PROCEDURE,
            None,
        ),
        (
            "Maintenance Schedule",
            "Replace the hydraulic filter every 500 hours.",
            ChunkType.MAINTENANCE_INTERVAL,
            None,
        ),
        (
            "Safety Warnings",
            "Warning: disconnect power before opening the housing.",
            ChunkType.SAFETY_WARNING,
            None,
        ),
        (
            "Troubleshooting",
            "Possible cause: low voltage. Corrective action: verify the supply.",
            ChunkType.TROUBLESHOOTING,
            None,
        ),
        (
            "Electrical Specifications",
            "Operating limits: 24 V, 3 A, 50 Hz.",
            ChunkType.TECHNICAL_SPECIFICATION,
            ["table_001"],
        ),
        (
            "Installation",
            "Install the bracket, align the housing, and secure the bolts.",
            ChunkType.INSTALLATION_INSTRUCTION,
            None,
        ),
        (
            "Operation",
            "Turn on the controller and operate the pump at nominal load.",
            ChunkType.OPERATION_INSTRUCTION,
            None,
        ),
        (
            "Certificate of Conformity",
            "This device complies with IEC 61010 and CE requirements.",
            ChunkType.CERTIFICATION_INFO,
            None,
        ),
    ],
)
def test_chunk_type_resolver_detects_semantic_chunk_types(
    section_title: str,
    text: str,
    expected_chunk_type: ChunkType,
    table_ids: list[str] | None,
) -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title=section_title,
                text=text,
                table_ids=table_ids,
            )
        ]
    )

    assert chunk_type == expected_chunk_type


def test_chunk_type_resolver_keeps_ambiguous_chunks_general() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Overview",
                text="Install and operate the module after setup.",
            )
        ]
    )

    assert chunk_type == ChunkType.GENERAL


def test_chunk_type_resolver_preserves_special_chunk_types() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Assembly View",
                text="Figure: Exploded assembly view.",
                chunk_type=ChunkType.DRAWING_REFERENCE,
            )
        ]
    )

    assert chunk_type == ChunkType.DRAWING_REFERENCE


def test_section_merge_policy_flushes_on_conflicting_semantic_sections() -> None:
    policy = SectionMergePolicy(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
        min_section_text_length=20,
    )
    current_fragment = make_fragment(
        section_id="sec_intro",
        section_title="Procedure",
        section_path=["Manual", "Procedure"],
        text="Follow the procedure to service the assembly.",
        token_count=40,
    )
    next_fragment = make_fragment(
        section_id="sec_specs",
        section_title="Electrical Specifications",
        section_path=["Manual", "Procedure", "Electrical Specifications"],
        text="Operating limits: 24 V, 3 A, 50 Hz.",
        token_count=24,
        parent_section_id="sec_intro",
        table_ids=["table_001"],
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is True
