from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_context_qualifier import (
    extract_local_reference_context,
)


def test_extracts_only_the_sentence_containing_the_match() -> None:
    content = (
        "This is unrelated background text. "
        "Refer to section 5.2 for calibration steps. "
        "This trailing sentence is also unrelated."
    )
    match_start = content.index("Refer to section 5.2")
    match_end = match_start + len("Refer to section 5.2")

    local_context = extract_local_reference_context(content, (match_start, match_end))

    assert local_context.strip() == "Refer to section 5.2 for calibration steps."


def test_does_not_leak_an_anchor_from_a_different_sentence_in_the_same_chunk() -> None:
    # The core locality concern: an external anchor in one sentence must
    # not contaminate qualification of an internal reference in another
    # sentence of the same chunk.
    content = (
        "Refer to section 5.2 for calibration steps. "
        "This procedure also mirrors the ISO 9001 standard for reference."
    )
    match_start = content.index("Refer to section 5.2")
    match_end = match_start + len("Refer to section 5.2")

    local_context = extract_local_reference_context(content, (match_start, match_end))

    assert "iso" not in local_context.lower()
    assert "standard" not in local_context.lower()


def test_falls_back_to_the_whole_content_when_there_is_only_one_sentence() -> None:
    content = "Refer to section 5.2 for calibration steps"
    match_start = content.index("Refer to section 5.2")
    match_end = match_start + len("Refer to section 5.2")

    local_context = extract_local_reference_context(content, (match_start, match_end))

    assert local_context == content


def test_extracts_the_correct_sentence_when_the_match_is_the_last_sentence() -> None:
    content = "First sentence here. Second sentence with section 6.5 in it."
    match_start = content.index("section 6.5")
    match_end = match_start + len("section 6.5")

    local_context = extract_local_reference_context(content, (match_start, match_end))

    assert local_context.strip() == "Second sentence with section 6.5 in it."
