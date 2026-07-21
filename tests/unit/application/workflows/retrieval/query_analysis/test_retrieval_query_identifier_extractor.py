from src.application.workflows.retrieval.query_analysis.retrieval_query_identifier_extractor import (
    RetrievalQueryIdentifierExtractor,
)

extractor = RetrievalQueryIdentifierExtractor()


def test_extract_returns_generic_identifier_tokens() -> None:
    assert extractor.extract("What does ordering code MK311007 mean?") == ["mk311007"]


def test_extract_returns_empty_list_for_no_identifiers() -> None:
    assert extractor.extract("What is the operating pressure?") == []


def test_extract_returns_empty_list_for_none() -> None:
    assert extractor.extract(None) == []


def test_extract_typed_recognizes_part_number_label() -> None:
    matches = extractor.extract_typed("What is part number HP-001?")
    assert len(matches) == 1
    assert matches[0].value == "hp-001"
    assert matches[0].identifier_type == "part_number"


def test_extract_typed_recognizes_abbreviated_part_number_label() -> None:
    matches = extractor.extract_typed("What is part no. HP-001?")
    assert matches[0].identifier_type == "part_number"
    assert matches[0].value == "hp-001"


def test_extract_typed_recognizes_slash_abbreviation() -> None:
    matches = extractor.extract_typed("What is p/n HP-001?")
    assert matches[0].identifier_type == "part_number"
    assert matches[0].value == "hp-001"


def test_extract_typed_recognizes_serial_number_label() -> None:
    matches = extractor.extract_typed("What is serial number FWC12?")
    assert matches[0].identifier_type == "serial_number"
    assert matches[0].value == "fwc12"


def test_extract_typed_recognizes_drawing_number_label() -> None:
    matches = extractor.extract_typed("Show drawing no. AB123-45")
    assert matches[0].identifier_type == "drawing_number"
    assert matches[0].value == "ab123-45"


def test_extract_typed_recognizes_ordering_code_label() -> None:
    matches = extractor.extract_typed("What does ordering code MK311007 mean?")
    assert matches[0].identifier_type == "order_code"
    assert matches[0].value == "mk311007"


def test_extract_typed_falls_back_to_unknown_for_untyped_identifier() -> None:
    matches = extractor.extract_typed("Where is item FWC12 located?")
    assert len(matches) == 1
    assert matches[0].value == "fwc12"
    assert matches[0].identifier_type == "unknown"


def test_extract_typed_does_not_duplicate_value_claimed_by_typed_pattern() -> None:
    matches = extractor.extract_typed("What is part number HP-001?")
    values = [match.value for match in matches]
    assert values.count("hp-001") == 1


def test_extract_typed_returns_empty_list_for_no_identifiers() -> None:
    assert extractor.extract_typed("What is the operating pressure?") == []


def test_extract_typed_returns_empty_list_for_none() -> None:
    assert extractor.extract_typed(None) == []
