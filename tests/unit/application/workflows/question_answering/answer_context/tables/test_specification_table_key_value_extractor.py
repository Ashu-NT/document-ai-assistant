from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTable,
    AnswerTableRow,
)
from src.application.workflows.question_answering.answer_context.tables.specification_table_key_value_extractor import (
    SpecificationTableKeyValueExtractor,
)


def test_extractor_reads_semantic_specification_projection_as_key_values() -> None:
    extractor = SpecificationTableKeyValueExtractor()
    table = AnswerTable(
        source_number=1,
        chunk_id="chunk_specification",
        chunk_type="technical_specification",
        document_title=None,
        section_path=None,
        page_start=None,
        page_end=None,
        headers=["Label", "Value"],
        rows=[
            AnswerTableRow(
                source_row_index=1,
                cells=["Pressure range (Compact version)", "0...10 bar"],
            ),
            AnswerTableRow(
                source_row_index=2,
                cells=["Pressure range (Remote version)", "0...16 bar"],
            ),
        ],
        table_kind="specification_matrix",
        column_roles={0: "label", 1: "value"},
    )

    key_values = extractor.extract(
        [table],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert [(item.key, item.value) for item in key_values] == [
        ("Pressure range (Compact version)", "0...10 bar"),
        ("Pressure range (Remote version)", "0...16 bar"),
    ]
