from src.application.services.answer_generation.formatting.identifier_answer_renderer import (
    IdentifierAnswerRenderer,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerKeyValue,
    StructuredAnswerContext,
)
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier


def _make_identifier(
    *,
    identifier_id: str = "id_001",
    raw_value: str = "HP-001",
    identifier_type: IdentifierType = IdentifierType.PART_NUMBER,
    document_id: str = "doc_1",
) -> Identifier:
    return Identifier(
        identifier_id=identifier_id,
        document_id=document_id,
        raw_value=raw_value,
        identifier_type=identifier_type,
    )


def _make_key_value(
    *,
    key: str = "Part Number",
    value: str = "HP-002",
    source_number: int = 1,
) -> AnswerKeyValue:
    return AnswerKeyValue(key=key, value=value, unit=None, source_number=source_number)


def test_render_returns_none_for_unsupported_intent() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        structured_context=None,
        resolved_identifiers=[_make_identifier()],
    )

    assert result is None


def test_render_returns_none_when_no_identifiers_available() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[],
    )

    assert result is None


def test_render_groups_single_identifier_type() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[_make_identifier(raw_value="HP-001")],
    )

    assert result is not None
    assert "Part Numbers:" in result
    assert "- HP-001" in result


def test_render_groups_multiple_identifier_types_in_fixed_order() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="List the part number and manufacturer",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[
            _make_identifier(
                identifier_id="id_1",
                raw_value="ACME Corp",
                identifier_type=IdentifierType.MANUFACTURER_NAME,
            ),
            _make_identifier(
                identifier_id="id_2",
                raw_value="HP-001",
                identifier_type=IdentifierType.PART_NUMBER,
            ),
        ],
    )

    assert result is not None
    part_index = result.index("Part Numbers:")
    manufacturer_index = result.index("Manufacturers:")
    assert part_index < manufacturer_index


def test_render_distinguishes_manufacturers_from_suppliers() -> None:
    """Manufacturer and supplier are now distinct identifier types with their
    own labels/groups — they must not be merged into a single "Manufacturers
    / Suppliers" bucket, and a question mentioning only "supplier" must not
    also surface manufacturer values."""
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="List the manufacturer and supplier",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[
            _make_identifier(
                identifier_id="id_1",
                raw_value="ACME Corp",
                identifier_type=IdentifierType.MANUFACTURER_NAME,
            ),
            _make_identifier(
                identifier_id="id_2",
                raw_value="FMD Rotterdam",
                identifier_type=IdentifierType.SUPPLIER_NAME,
            ),
        ],
    )

    assert result is not None
    assert "Manufacturers:" in result
    assert "Suppliers:" in result
    assert "ACME Corp" in result
    assert "FMD Rotterdam" in result
    manufacturer_index = result.index("Manufacturers:")
    supplier_index = result.index("Suppliers:")
    assert manufacturer_index < supplier_index


def test_render_supplier_only_question_excludes_manufacturers() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="Who is the supplier?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[
            _make_identifier(
                identifier_id="id_1",
                raw_value="ACME Corp",
                identifier_type=IdentifierType.MANUFACTURER_NAME,
            ),
            _make_identifier(
                identifier_id="id_2",
                raw_value="FMD Rotterdam",
                identifier_type=IdentifierType.SUPPLIER_NAME,
            ),
        ],
    )

    assert result is not None
    assert "Suppliers:" in result
    assert "FMD Rotterdam" in result
    assert "Manufacturers:" not in result
    assert "ACME Corp" not in result


def test_render_filters_to_types_mentioned_in_question() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the serial number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[
            _make_identifier(
                identifier_id="id_1",
                raw_value="HP-001",
                identifier_type=IdentifierType.PART_NUMBER,
            ),
            _make_identifier(
                identifier_id="id_2",
                raw_value="SN-9999",
                identifier_type=IdentifierType.SERIAL_NUMBER,
            ),
        ],
    )

    assert result is not None
    assert "Serial Numbers:" in result
    assert "Part Numbers:" not in result
    assert "SN-9999" in result


def test_render_returns_none_when_question_filter_excludes_all_identifiers() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the drawing number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[_make_identifier(identifier_type=IdentifierType.PART_NUMBER)],
    )

    assert result is None


def test_render_skips_unknown_identifier_type() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What identifiers are listed?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[_make_identifier(identifier_type=IdentifierType.UNKNOWN)],
    )

    assert result is None


def test_render_deduplicates_case_insensitive_within_same_type() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[
            _make_identifier(identifier_id="id_1", raw_value="HP-001"),
            _make_identifier(identifier_id="id_2", raw_value="hp-001"),
        ],
    )

    assert result is not None
    assert result.count("HP-001") + result.count("hp-001") == 1


def test_render_merges_structured_context_key_values() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=StructuredAnswerContext(
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            key_values=[_make_key_value(key="Part Number", value="HP-002")],
        ),
        resolved_identifiers=[_make_identifier(raw_value="HP-001")],
    )

    assert result is not None
    assert "HP-001" in result
    assert "HP-002" in result


def test_render_deduplicates_between_identifiers_and_key_values() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=StructuredAnswerContext(
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            key_values=[_make_key_value(key="Part Number", value="HP-001")],
        ),
        resolved_identifiers=[_make_identifier(raw_value="HP-001")],
    )

    assert result is not None
    assert result.count("HP-001") == 1


def test_render_ignores_key_value_with_unrecognized_key() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What identifiers are listed?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=StructuredAnswerContext(
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            key_values=[_make_key_value(key="Pressure Rating", value="16 bar")],
        ),
        resolved_identifiers=[],
    )

    assert result is None


def test_render_cleans_whitespace_in_values() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[_make_identifier(raw_value="  HP-001   Rev A  ")],
    )

    assert result is not None
    assert "- HP-001 Rev A" in result


def test_render_skips_blank_identifier_value() -> None:
    renderer = IdentifierAnswerRenderer()

    result = renderer.render(
        question="What is the part number?",
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        structured_context=None,
        resolved_identifiers=[_make_identifier(raw_value="   ")],
    )

    assert result is None
