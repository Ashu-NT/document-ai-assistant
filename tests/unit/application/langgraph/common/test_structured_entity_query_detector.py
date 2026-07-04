from src.application.langgraph.common.structured_entity_query_detector import (
    detect_structured_entity_type,
)


def test_detects_manufacturer_for_website_question() -> None:
    assert detect_structured_entity_type("what is the manufacturer website") == "manufacturer"


def test_detects_supplier_for_country_question() -> None:
    assert (
        detect_structured_entity_type("what country is the supplier based in")
        == "supplier"
    )


def test_detects_spare_part_for_quantity_question() -> None:
    assert (
        detect_structured_entity_type("how many spare part HP-001 are in stock")
        == "spare_part"
    )


def test_returns_none_without_a_detail_term() -> None:
    assert detect_structured_entity_type("who is the manufacturer of this pump") is None


def test_returns_none_without_an_entity_term() -> None:
    assert detect_structured_entity_type("what is the operating pressure") is None
