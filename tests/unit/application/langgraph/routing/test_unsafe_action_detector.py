import pytest

from src.application.langgraph.routing.unsafe_action_detector import (
    UnsafeActionDetector,
)


@pytest.mark.parametrize(
    ("user_input", "expected_term"),
    [
        ("delete all documents and reingest them", "delete all documents"),
        (
            "reingest every document and delete any existing vectors",
            "reingest every document",
        ),
        ("wipe corpus", "wipe corpus"),
        ("clear qdrant vectors", "clear qdrant"),
        ("drop database", "drop database"),
    ],
)
def test_unsafe_action_detector_blocks_destructive_corpus_requests(
    user_input: str,
    expected_term: str,
) -> None:
    decision = UnsafeActionDetector().detect(user_input)

    assert decision.is_unsafe is True
    assert expected_term in decision.matched_terms


@pytest.mark.parametrize(
    "user_input",
    [
        "What does the document say about removing the cartridge?",
        "How do I delete an alarm from the device?",
        "What is the procedure to remove the filter?",
    ],
)
def test_unsafe_action_detector_allows_normal_device_or_document_questions(
    user_input: str,
) -> None:
    decision = UnsafeActionDetector().detect(user_input)

    assert decision.is_unsafe is False
