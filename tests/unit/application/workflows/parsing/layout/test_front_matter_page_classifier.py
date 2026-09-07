from src.application.workflows.parsing.layout.front_matter_page_classifier import (
    FrontMatterPageClassifier,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)


def _candidate(ref: str, page: int, label: str, text: str) -> PageLayoutCandidate:
    return PageLayoutCandidate(
        element_ref=ref,
        page_number=page,
        bbox=None,
        label=label,
        text=text,
    )


def test_initial_multi_page_document_index_defines_front_matter_boundary() -> None:
    candidates = [
        _candidate("cover", 1, "title", "Technical Operating Manual"),
        _candidate("index_1", 3, "document_index", "1 Introduction 9"),
        _candidate("index_2", 4, "document_index", "2 Safety 15"),
        _candidate("body", 5, "section_header", "1 Introduction"),
    ]

    result = FrontMatterPageClassifier().classify(candidates)

    assert result == {1, 3, 4}


def test_later_appendix_index_does_not_extend_initial_index_block() -> None:
    candidates = [
        _candidate("cover", 1, "title", "Technical Operating Manual"),
        _candidate("index_1", 2, "document_index", "1 Introduction 5"),
        _candidate("body", 3, "section_header", "1 Introduction"),
        _candidate("appendix_index", 40, "document_index", "Index"),
    ]

    result = FrontMatterPageClassifier().classify(candidates)

    assert result == {1, 2}
