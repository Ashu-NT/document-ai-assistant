from tests.unit.application.workflows.parsing.builders.chunking._test_chunk_type_resolver_support import (
    make_fragment,
)

from src.application.workflows.parsing.builders.chunking.builders import ChunkTypeResolver
from src.domain.common import ChunkType

# Regression guard for a real bug: this exact content (from
# KSB_FSD_A3000_E3000-L-400_DOCUMENTATION_rev4_MY COSMOS.pdf, page 2's
# orphaned right-hand TOC column) used to resolve to SAFETY_WARNING purely
# because "Automatic door lock and safety strip" is a listed section title
# containing the word "safety" -- not because this chunk is actually about
# a safety warning.
_REAL_TOC_REMNANT_CONTENT = (
    "................................\n"
    "1.10 Automatic door lock and safety strip\n"
    "2 Options\n"
    "...........\n"
    "................................\n"
    "..................\n"
    "6\n7\n8\n9"
)


def test_resolve_returns_general_for_a_real_toc_remnant_chunk_instead_of_safety_warning() -> None:
    resolver = ChunkTypeResolver()
    fragments = [
        make_fragment(
            section_title="Safety Instructions",
            section_path=["Fire Sliding Door A-60", "Safety Instructions"],
            text=_REAL_TOC_REMNANT_CONTENT,
        )
    ]

    result = resolver.resolve(fragments=fragments, content=_REAL_TOC_REMNANT_CONTENT)

    assert result == ChunkType.GENERAL


def test_resolve_still_classifies_genuine_safety_warning_content() -> None:
    resolver = ChunkTypeResolver()
    text = (
        "CAUTION: Before performing any maintenance, disconnect power supply "
        "completely.\nFailure to do so may result in serious injury.\n"
        "Warning: always wear protective gloves before handling internal "
        "components.\nDanger: hazard of electric shock if power is not "
        "isolated first."
    )
    fragments = [
        make_fragment(
            section_title="Safety Warnings",
            section_path=["Manual", "Safety Warnings"],
            text=text,
        )
    ]

    result = resolver.resolve(fragments=fragments, content=text)

    assert result == ChunkType.SAFETY_WARNING
