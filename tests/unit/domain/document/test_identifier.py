from src.domain.common import IdentifierType
from src.domain.document import Identifier


def test_identifier_normalizes_raw_value() -> None:
    identifier = Identifier(
        identifier_id="identifier_001",
        document_id="doc_001",
        raw_value=" HP-001 ",
        identifier_type=IdentifierType.PART_NUMBER,
    )

    assert identifier.normalized_value == "HP-001"


def test_identifier_uses_provided_normalized_value() -> None:
    identifier = Identifier(
        identifier_id="identifier_001",
        document_id="doc_001",
        raw_value="HP 001",
        normalized_value="HP001",
    )

    assert identifier.normalized_value == "HP001"