from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_type_markers import (
    is_toc_remnant_text,
)

# Exact real chunk content captured from a real document
# (KSB_FSD_A3000_E3000-L-400_DOCUMENTATION_rev4_MY COSMOS.pdf) -- page 2's
# right-hand TOC column was never recognized as a table by Docling at all,
# so it survived only as loose text and was misclassified as
# `safety_warning`/`certification_info` purely because it happens to
# contain a listed section title matching one of those keyword markers.

_REAL_CHUNK_1 = (
    "................................\n"
    "1.10 Automatic door lock and safety strip\n"
    "2 Options\n"
    "...........\n"
    "................................\n"
    "..................\n"
    "6\n7\n8\n9"
)

_REAL_CHUNK_2 = (
    "................................\n"
    "................................\n"
    "3 Function description\n"
    "................................\n"
    "...........\n"
    "..........................\n"
    ".............................................................................\n"
    "3.1 General arrangement\n"
    "................................\n"
    "...."
)

_REAL_CHUNK_3 = (
    "................................\n"
    "Passenger's safety\n"
    "................................\n"
    "Product quality\n"
    "..................\n"
    "................................\n"
    "................................\n"
    "................................\n"
    "................\n"
    "......................."
)


def test_is_toc_remnant_text_detects_real_chunk_with_numbered_headings_and_bare_pages() -> None:
    assert is_toc_remnant_text(_REAL_CHUNK_1)


def test_is_toc_remnant_text_detects_real_chunk_with_mostly_dot_leader_lines() -> None:
    assert is_toc_remnant_text(_REAL_CHUNK_2)


def test_is_toc_remnant_text_detects_real_chunk_with_plain_title_fragments() -> None:
    assert is_toc_remnant_text(_REAL_CHUNK_3)


def test_is_toc_remnant_text_returns_false_for_none() -> None:
    assert not is_toc_remnant_text(None)


def test_is_toc_remnant_text_returns_false_for_short_text() -> None:
    assert not is_toc_remnant_text("Warning: disconnect power before servicing.")


def test_is_toc_remnant_text_returns_false_for_genuine_safety_warning_prose() -> None:
    text = (
        "CAUTION: Before performing any maintenance, disconnect power supply "
        "completely.\nFailure to do so may result in serious injury.\n"
        "Warning: always wear protective gloves before handling internal "
        "components.\nSee section 4.2 for further details."
    )

    assert not is_toc_remnant_text(text)


def test_is_toc_remnant_text_returns_false_for_ordinary_numbered_instructions() -> None:
    # Ordinary "N. instruction" numbered steps (period directly after the
    # digit, no second digit) must not be mistaken for TOC section
    # numbering ("N Title"/"N.M Title", no period-space after the number).
    text = (
        "1. Ensure main power is off.\n"
        "2. Remove the access panel.\n"
        "3. Inspect for visible damage.\n"
        "4. Reinstall the panel and restore power."
    )

    assert not is_toc_remnant_text(text)
