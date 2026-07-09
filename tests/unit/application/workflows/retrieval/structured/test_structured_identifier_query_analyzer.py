import pytest

from src.application.workflows.retrieval.structured.structured_identifier_query_analyzer import (
    StructuredIdentifierQueryAnalyzer,
)
from src.domain.common import IdentifierType


@pytest.fixture
def analyzer() -> StructuredIdentifierQueryAnalyzer:
    return StructuredIdentifierQueryAnalyzer()


def test_looks_like_inventory_query_true_for_listing_verb_and_marker(analyzer) -> None:
    assert analyzer.looks_like_inventory_query("list all part numbers") is True


def test_looks_like_inventory_query_false_without_listing_verb(analyzer) -> None:
    assert analyzer.looks_like_inventory_query("part numbers") is False


def test_looks_like_inventory_query_false_when_query_contains_identifier_value(
    analyzer,
) -> None:
    assert analyzer.looks_like_inventory_query("list part number MK311007") is False


def test_looks_like_inventory_query_false_for_empty_or_missing_query(analyzer) -> None:
    assert analyzer.looks_like_inventory_query("") is False
    assert analyzer.looks_like_inventory_query(None) is False


def test_requested_identifier_types_matches_multiple_markers(analyzer) -> None:
    types = analyzer.requested_identifier_types(
        "give me all part numbers and serial numbers"
    )

    assert IdentifierType.PART_NUMBER in types
    assert IdentifierType.SERIAL_NUMBER in types


def test_requested_identifier_types_empty_when_no_marker_present(analyzer) -> None:
    assert analyzer.requested_identifier_types("how does the pump work") == []


def test_contains_identifier_value_delegates_to_shared_pattern(analyzer) -> None:
    assert analyzer.contains_identifier_value("Ordering code MK311007") is True
    assert analyzer.contains_identifier_value("no identifiers here") is False
