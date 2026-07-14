from src.application.services.answer_generation.formatting.renderers import (
    TroubleshootingRenderer,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
    AnswerStructuredEntity,
    StructuredAnswerContext,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
    AnswerTableRow,
)


def test_renderer_prefers_typed_troubleshooting_table_rows_over_sparse_entities() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.TROUBLESHOOTING,
        sources=[
            AnswerSource(
                source_number=1,
                chunk_id="chunk_trouble",
                page_start=89,
                page_end=89,
            )
        ],
        tables=[
            AnswerTable(
                source_number=1,
                chunk_id="chunk_trouble",
                chunk_type="troubleshooting",
                document_title="Manual",
                section_path="Troubleshooting",
                page_start=89,
                page_end=89,
                headers=["Symptom", "Cause", "Remedy"],
                rows=[
                    AnswerTableRow(
                        source_row_index=1,
                        cells=[
                            "(1) The motor does not start",
                            "Motor overload protection cuts in",
                            "Check the power supply and make sure that the shaft is free.",
                        ],
                        cells_by_header={
                            "Symptom": "(1) The motor does not start",
                            "Cause": "Motor overload protection cuts in",
                            "Remedy": "Check the power supply and make sure that the shaft is free.",
                        },
                    )
                ],
                table_kind="troubleshooting_table",
            )
        ],
        structured_entities=[
            AnswerStructuredEntity(
                entity_type="troubleshooting",
                entity_id="trouble_001",
                source_chunk_id="chunk_trouble",
                fields={
                    "symptom": "(1) The motor does not start",
                    "cause": "1a)",
                    "remedy": "1a)",
                },
            )
        ],
    )

    answer = TroubleshootingRenderer().render(
        answer_intent=AnswerIntent.TROUBLESHOOTING,
        structured_context=context,
    )

    assert answer is not None
    assert "Motor overload" in answer
    assert "Check the power supply" in answer
    assert "| 1a)" not in answer
    assert "p.89" in answer
