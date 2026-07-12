from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.workflows.question_answering.answer_context.key_value_extractor import (
    KeyValueExtractor,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerSource,
)


def _make_source(
    *,
    content: str = "",
    table_rows: list[list[str]] | None = None,
    chunk_type: str | None = None,
) -> AnswerSource:
    return AnswerSource(
        source_number=1,
        chunk_id="chunk_001",
        content=content,
        table_rows=table_rows,
        chunk_type=chunk_type,
    )


def test_extract_finds_key_values_from_structured_rows() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        content="",
        table_rows=[["Parameter", "Value"], ["Design pressure", "10 bar"]],
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert len(key_values) == 1
    assert key_values[0].key == "Design pressure"
    assert key_values[0].value == "10 bar"


def test_extract_does_not_duplicate_when_rows_and_content_agree() -> None:
    extractor = KeyValueExtractor()
    content = "| Design pressure | 10 bar |"
    source = _make_source(
        content=content,
        table_rows=[["Design pressure", "10 bar"]],
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert len(key_values) == 1


def test_extract_ignores_table_rows_for_unsupported_intent() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        table_rows=[["Design pressure", "10 bar"]],
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.PROCEDURE_STEPS,
    )

    assert key_values == []


def test_extract_excludes_identifier_rows_from_specification_summary() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        table_rows=[
            ["Parameter", "Value"],
            ["Serial Number", "D4093386"],
            ["Power", "3.0 kW"],
        ]
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert [(item.key, item.value) for item in key_values] == [("Power", "3.0 kW")]


def test_extract_identifier_lookup_keeps_identifier_rows_from_structured_table() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        table_rows=[
            ["Parameter", "Value"],
            ["Serial Number", "D4093386"],
            ["Part Number", "A00103"],
            ["Power", "3.0 kW"],
        ]
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert [(item.key, item.value) for item in key_values] == [
        ("Serial Number", "D4093386"),
        ("Part Number", "A00103"),
    ]


def test_extract_uses_generic_record_table_headers_as_fields() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        chunk_type="certification_info",
        table_rows=[
            ["Quantity", "Description", "Size"],
            ["2", "Flexible hose", "DN25"],
        ]
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.CERTIFICATION_SUMMARY,
    )

    assert [(item.key, item.value) for item in key_values] == [
        ("Quantity", "2"),
        ("Description", "Flexible hose"),
        ("Size", "DN25"),
    ]


def test_extract_does_not_treat_narrative_sentence_as_power_key_value() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        content="The power supply may not vary from the contract specifications of the system."
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert key_values == []
