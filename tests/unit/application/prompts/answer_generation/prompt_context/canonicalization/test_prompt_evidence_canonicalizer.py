from src.application.prompts.answer_generation.prompt_context.canonicalization import (
    PromptEvidenceCanonicalizer,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptEntityView,
    PromptSourceView,
    PromptTableRowView,
    PromptTableView,
)
from src.application.services.answer_generation import AnswerIntent
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
)


def test_canonicalizer_removes_entity_derived_key_values_and_omits_payload_content() -> None:
    bundle = PromptContextBundle(
        answer_intent_value=AnswerIntent.IDENTIFIER_LOOKUP.value,
        source_count=1,
        sources=[
            PromptSourceView(
                source_number=1,
                chunk_id="chunk_001",
                document_title="Manual",
                section_path="Spare Parts",
                content="Part Number: HP-001",
            )
        ],
        appendix_sources=[
            PromptSourceView(
                source_number=1,
                chunk_id="chunk_001",
                document_title="Manual",
                section_path="Spare Parts",
                content="Part Number: HP-001",
            )
        ],
        key_values=[
            AnswerKeyValue(
                key="Part Number",
                value="HP-001",
                unit=None,
                source_number=1,
            )
        ],
        entities=[
            PromptEntityView(
                entity_type="spare_part",
                entity_id="sp_001",
                source_chunk_id="chunk_001",
                fields={"part_number": "HP-001", "description": "Hydraulic filter"},
            )
        ],
    )

    canonicalized = PromptEvidenceCanonicalizer().canonicalize(bundle)

    assert canonicalized is not None
    assert canonicalized.key_values == []
    assert canonicalized.sources[0].content == ""
    assert canonicalized.appendix_sources[0].content == "Part Number: HP-001"
    assert canonicalized.diagnostics["prompt_canonicalized_key_values_removed"] == 1


def test_canonicalizer_prefers_key_values_over_table_rows_for_specification_summary() -> None:
    source = PromptSourceView(
        source_number=1,
        chunk_id="chunk_001",
        document_title="Certificate",
        section_path="Particulars",
        content="Test pressure: 700 bar",
        table_rows=[["Parameter", "Value"], ["Test pressure", "700 bar"]],
    )
    bundle = PromptContextBundle(
        answer_intent_value=AnswerIntent.SPECIFICATION_SUMMARY.value,
        source_count=1,
        sources=[source],
        appendix_sources=[source],
        key_values=[
            AnswerKeyValue(
                key="Test pressure",
                value="700 bar",
                unit="bar",
                source_number=1,
            )
        ],
        tables=[
            PromptTableView(
                table_id="chunk_001:table",
                table_type="specification_table",
                source_number=1,
                chunk_id="chunk_001",
                headers=["Parameter", "Value"],
                rows=[
                    PromptTableRowView(
                        source_row_index=1,
                        cells=["Test pressure", "700 bar"],
                        cells_by_header={
                            "Parameter": "Test pressure",
                            "Value": "700 bar",
                        },
                    )
                ],
            )
        ],
    )

    canonicalized = PromptEvidenceCanonicalizer().canonicalize(bundle)

    assert canonicalized is not None
    assert canonicalized.sources[0].table_rows is None
    assert canonicalized.appendix_sources[0].table_rows == [
        ["Parameter", "Value"],
        ["Test pressure", "700 bar"],
    ]


def test_canonicalizer_promotes_table_summary_rows_to_top_level_tables() -> None:
    source = PromptSourceView(
        source_number=1,
        chunk_id="chunk_001",
        document_title="Manual",
        section_path="Valve List",
        content="| Tag | Part No |",
        table_rows=[["Tag", "Part No"], ["V.00.01.01", "A00103"]],
    )
    bundle = PromptContextBundle(
        answer_intent_value=AnswerIntent.TABLE_SUMMARY.value,
        source_count=1,
        sources=[source],
        appendix_sources=[source],
        tables=[
            PromptTableView(
                table_id="chunk_001:table",
                table_type="general_table",
                source_number=1,
                chunk_id="chunk_001",
                headers=["Tag", "Part No"],
                rows=[
                    PromptTableRowView(
                        source_row_index=1,
                        cells=["V.00.01.01", "A00103"],
                        cells_by_header={
                            "Tag": "V.00.01.01",
                            "Part No": "A00103",
                        },
                    )
                ],
            )
        ],
    )

    canonicalized = PromptEvidenceCanonicalizer().canonicalize(bundle)

    assert canonicalized is not None
    assert canonicalized.sources[0].table_rows is None
    assert canonicalized.tables[0].headers == ["Tag", "Part No"]
    assert canonicalized.tables[0].rows[0].cells_by_header == {
        "Tag": "V.00.01.01",
        "Part No": "A00103",
    }
    assert canonicalized.appendix_sources[0].table_rows == [
        ["Tag", "Part No"],
        ["V.00.01.01", "A00103"],
    ]
