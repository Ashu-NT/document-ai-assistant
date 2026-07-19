from src.application.prompts.answer_generation.prompt_context.projectors import (
    PromptContextProjector,
)
from src.application.services.answer_generation import AnswerIntent
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
    AnswerRelationship,
    AnswerStructuredEntity,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
    StructuredAnswerContext,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
    AnswerTableRow,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    chunk_id: str = "chunk_001",
    content: str = "Replace hydraulic filter every 1000 hours.",
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["Maintenance", "Schedule"],
        source=SourceLocation(page_start=5, page_end=5),
    )


def test_projector_maps_structured_answer_context_into_prompt_bundle() -> None:
    context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[_make_chunk()],
    )
    context.structured_entities.append(
        AnswerStructuredEntity(
            entity_type="maintenance_task",
            entity_id="task_001",
            fields={"title": "Replace hydraulic filter"},
            relationships=[
                AnswerRelationship(
                    relationship_type="task_uses_procedure",
                    direction="outgoing",
                    status="accepted",
                    target_entity_type="procedure",
                    target_entity_id="procedure_001",
                    target_entity_fields={"steps": ["Depressurize the line."]},
                )
            ],
        )
    )

    bundle = PromptContextProjector().project(context)

    assert bundle is not None
    assert bundle.answer_intent_value == "maintenance_summary"
    assert bundle.source_count == 1
    assert bundle.sources[0].document_title == "Current document"
    assert bundle.sources[0].section_path == "Maintenance > Schedule"
    assert bundle.entities[0].entity_type == "maintenance_task"
    assert bundle.entities[0].relationships[0].target_entity_id == "procedure_001"
    assert bundle.relationship_edges[0].source_entity_id == "task_001"
    assert bundle.relationship_edges[0].target_entity_id == "procedure_001"
    assert bundle.relationship_families[0].anchor_entity_id == "task_001"
    assert bundle.relationship_families[0].related_entity_ids == ["procedure_001"]
    assert bundle.source_families[0].direct_source_numbers == [1]
    assert bundle.section_topology[0].section_name == "Schedule"
    assert bundle.maintenance_entries


def test_projector_builds_first_class_table_views_from_source_rows() -> None:
    chunk = RetrievedChunk(
        chunk_id="chunk_002",
        document_id="doc_001",
        content="Test pressure: 700 bar",
        score=0.8,
        retrieval_source="dense",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Certificate", "Particulars"],
        source=SourceLocation(page_start=7, page_end=7),
        metadata={
            "table_rows_json": '[["Parameter","Value"],["Test pressure","700 bar"]]'
        },
    )
    context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[chunk],
    )

    bundle = PromptContextProjector().project(context)

    assert bundle is not None
    assert len(bundle.tables) == 1
    assert bundle.tables[0].table_type == "certification_table"
    assert bundle.tables[0].headers == ["Parameter", "Value"]
    assert bundle.tables[0].rows[0].cells == ["Test pressure", "700 bar"]
    assert bundle.tables[0].rows[0].cells_by_header == {
        "Parameter": "Test pressure",
        "Value": "700 bar",
    }
    assert bundle.sources[0].table_rows is None


def test_projector_prefers_prebuilt_answer_tables_when_available() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        sources=[
            AnswerSource(
                source_number=1,
                chunk_id="chunk_sched",
                document_id="doc_001",
                document_title="FWC12 Manual",
                section_path="Maintenance > Schedule",
                page_start=58,
                page_end=59,
                table_rows=[["Legacy", "Rows"]],
            )
        ],
        tables=[
            AnswerTable(
                source_number=1,
                chunk_id="chunk_sched",
                chunk_type="maintenance_interval",
                document_title="FWC12 Manual",
                section_path="Maintenance > Schedule",
                page_start=58,
                page_end=59,
                headers=["Task", "Interval"],
                rows=[
                    AnswerTableRow(
                        source_row_index=1,
                        cells=["Inspect basket", "Monthly"],
                        cells_by_header={
                            "Task": "Inspect basket",
                            "Interval": "Monthly",
                        },
                    )
                ],
                table_kind=TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE,
                table_category="maintenance_interval_table",
            )
        ],
        source_count=1,
    )

    bundle = PromptContextProjector().project(context)

    assert bundle is not None
    assert len(bundle.tables) == 1
    assert bundle.tables[0].table_type == "maintenance_table"
    assert bundle.tables[0].headers == ["Task", "Interval"]
    assert bundle.tables[0].rows[0].cells == ["Inspect basket", "Monthly"]


def test_projector_rescues_a_source_whose_prebuilt_table_projection_failed() -> None:
    """Finding F8: when one source's AnswerTable comes out empty (dropped by
    build_from_answer_tables) while a DIFFERENT source's table projects
    fine, the failed source's raw table_rows must still get a fallback
    chance via build() -- not silently vanish just because `tables` overall
    isn't empty."""
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[
            AnswerSource(
                source_number=1,
                chunk_id="chunk_failed",
                document_id="doc_001",
                document_title="FWC12 Manual",
                section_path="Spare Parts",
                page_start=10,
                page_end=10,
                table_rows=[["Part No", "Description"], ["HP-001", "Seal kit"]],
            ),
            AnswerSource(
                source_number=2,
                chunk_id="chunk_ok",
                document_id="doc_001",
                document_title="FWC12 Manual",
                section_path="Maintenance > Schedule",
                page_start=58,
                page_end=59,
            ),
        ],
        tables=[
            # Simulates AnswerTableProjector._build_table() failing for this
            # source: an AnswerTable placeholder with no headers/rows at all,
            # which build_from_answer_tables() silently drops.
            AnswerTable(
                source_number=1,
                chunk_id="chunk_failed",
                chunk_type="spare_parts_table",
                document_title="FWC12 Manual",
                section_path="Spare Parts",
                page_start=10,
                page_end=10,
                headers=[],
                rows=[],
                table_kind=TableQueryStrategy.SPARE_PARTS_TABLE,
                table_category="spare_parts_table",
            ),
            AnswerTable(
                source_number=2,
                chunk_id="chunk_ok",
                chunk_type="maintenance_interval",
                document_title="FWC12 Manual",
                section_path="Maintenance > Schedule",
                page_start=58,
                page_end=59,
                headers=["Task", "Interval"],
                rows=[
                    AnswerTableRow(
                        source_row_index=1,
                        cells=["Inspect basket", "Monthly"],
                        cells_by_header={
                            "Task": "Inspect basket",
                            "Interval": "Monthly",
                        },
                    )
                ],
                table_kind=TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE,
                table_category="maintenance_interval_table",
            ),
        ],
        source_count=2,
    )

    bundle = PromptContextProjector().project(context)

    assert bundle is not None
    table_chunk_ids = {table.chunk_id for table in bundle.tables}
    assert table_chunk_ids == {"chunk_failed", "chunk_ok"}
    rescued = next(t for t in bundle.tables if t.chunk_id == "chunk_failed")
    assert rescued.headers == ["Part No", "Description"]
    assert rescued.rows[0].cells == ["HP-001", "Seal kit"]
