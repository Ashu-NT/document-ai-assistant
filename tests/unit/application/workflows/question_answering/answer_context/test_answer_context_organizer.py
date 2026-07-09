from src.application.services.answer_generation import AnswerIntent
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.document.value_objects import ChunkStatistics
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    *,
    chunk_id: str,
    content: str,
    chunk_type: ChunkType = ChunkType.TECHNICAL_SPECIFICATION,
    section_path: list[str] | None = None,
    retrieval_source: str = "dense",
    section_id: str | None = None,
    statistics: ChunkStatistics | None = None,
    identifier_values: list[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source=retrieval_source,
        chunk_type=chunk_type,
        section_id=section_id,
        section_path=section_path or ["Certificate", "Particulars"],
        source=SourceLocation(page_start=2, page_end=2),
        statistics=statistics,
        identifier_values=identifier_values or [],
        metadata=metadata or {},
    )


def test_context_organizer_extracts_spec_key_values_and_preserves_metadata() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[
            _make_chunk(
                chunk_id="chunk_001",
                content="Test pressure: 700 bar\nDesign pressure: 350 bar\nSize: DN 8",
            )
        ],
    )

    assert context.source_count == 1
    assert context.sources[0].source_number == 1
    assert context.sources[0].document_id == "doc_001"
    assert context.sources[0].page_start == 2
    assert context.sources[0].section_path == "Certificate > Particulars"
    assert context.sources[0].content.startswith("Test pressure")
    assert ("Test pressure", "700 bar") in {
        (item.key, item.value) for item in context.key_values
    }
    assert ("Design pressure", "350 bar") in {
        (item.key, item.value) for item in context.key_values
    }


def test_context_organizer_enriches_source_with_retrieval_metadata() -> None:
    """Plan section 9.1/4.1: AnswerSource should carry the retrieval/chunk
    metadata that already existed on RetrievedChunk instead of formatting
    code having to re-derive it later."""
    organizer = AnswerContextOrganizer()
    statistics = ChunkStatistics(char_count=42, token_count_estimate=8)
    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[
            _make_chunk(
                chunk_id="chunk_001",
                content="Test pressure: 700 bar",
                retrieval_source="sql_keyword",
                section_id="sec_042",
                statistics=statistics,
                identifier_values=["HP-001"],
                metadata={
                    "dedup_collapsed_chunk_ids": "chunk_a,chunk_b",
                    "sql_keyword_source_score": "12.0",
                },
            )
        ],
    )

    source = context.sources[0]
    assert source.retrieval_source == "sql_keyword"
    assert source.section_id == "sec_042"
    assert source.statistics is statistics
    assert source.identifier_values == ["HP-001"]
    assert source.metadata["sql_keyword_source_score"] == "12.0"
    assert source.collapsed_chunk_ids == ["chunk_a", "chunk_b"]


def test_context_organizer_defaults_collapsed_chunk_ids_when_not_deduplicated() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[_make_chunk(chunk_id="chunk_001", content="Test pressure: 700 bar")],
    )

    assert context.sources[0].collapsed_chunk_ids == []


def test_context_organizer_normalizes_collapsed_chunk_ids_from_csv_metadata() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[
            _make_chunk(
                chunk_id="chunk_001",
                content="Test pressure: 700 bar",
                metadata={
                    "dedup_collapsed_chunk_ids": " chunk_a,chunk_b ,  , chunk_c ",
                },
            )
        ],
    )

    assert context.sources[0].collapsed_chunk_ids == [
        "chunk_a",
        "chunk_b",
        "chunk_c",
    ]


def test_context_organizer_groups_sources_by_chunk_type_and_section() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.PROCEDURE_STEPS,
        chunks=[
            _make_chunk(
                chunk_id="chunk_a",
                content="1. Stop the pump",
                chunk_type=ChunkType.OPERATION_INSTRUCTION,
                section_path=["Operation", "Stopping"],
            ),
            _make_chunk(
                chunk_id="chunk_b",
                content="2. Isolate the line",
                chunk_type=ChunkType.OPERATION_INSTRUCTION,
                section_path=["Operation", "Stopping"],
            ),
        ],
    )

    assert len(context.source_groups) == 1
    assert context.source_groups[0].chunk_type == "operation_instruction"
    assert len(context.section_groups) == 1
    assert context.section_groups[0].section_path == "Operation > Stopping"


def test_context_organizer_extracts_structured_maintenance_entries() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[
            _make_chunk(
                chunk_id="chunk_maintenance",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
                section_path=["Maintenance", "Schedule"],
                content=(
                    "Replace cartridge filters every 1000 operating hours.\n"
                    "Inspect regulating valves."
                ),
            )
        ],
    )

    assert len(context.maintenance_entries) == 2
    assert context.maintenance_entries[0].task == "Replace cartridge filters"
    assert context.maintenance_entries[0].description == "Replace cartridge filters"
    assert context.maintenance_entries[0].interval == "every 1000 operating hours"
    assert context.maintenance_entries[0].component == "cartridge filters"
    assert context.maintenance_entries[0].source_number == 1
    assert context.maintenance_entries[0].source_numbers == [1]
    assert context.maintenance_entries[0].page_start == 2
    assert context.maintenance_entries[0].section_path == "Maintenance > Schedule"
    assert context.maintenance_entries[1].task == "Inspect regulating valves"
    assert context.maintenance_entries[1].interval == "Not specified"
    assert context.diagnostics["maintenance_items_found"] == 2
    assert context.diagnostics["maintenance_items_with_interval"] == 1
    assert context.diagnostics["maintenance_items_without_interval"] == 1
    assert context.diagnostics["maintenance_items_merged"] == 0


def test_context_organizer_merges_duplicate_maintenance_tasks_and_references() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[
            _make_chunk(
                chunk_id="chunk_dup_a",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
                section_path=["Preventive Maintenance", "Gearbox"],
                content="Check gearbox every 6 months.",
            ),
            _make_chunk(
                chunk_id="chunk_dup_b",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
                section_path=["Preventive Maintenance", "Lubrication"],
                content="Check gearbox for leaks every 6 months.",
            ),
        ],
    )

    assert len(context.maintenance_entries) == 1
    entry = context.maintenance_entries[0]
    assert entry.task == "Check gearbox for leaks"
    assert entry.interval == "every 6 months"
    assert entry.source_numbers == [1, 2]
    assert entry.section_paths == [
        "Preventive Maintenance > Gearbox",
        "Preventive Maintenance > Lubrication",
    ]
    assert len(entry.references) == 2
    assert context.diagnostics["maintenance_items_merged"] == 1


def test_context_organizer_cleans_placeholder_maintenance_values() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[
            _make_chunk(
                chunk_id="chunk_table",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
                section_path=["Maintenance", "Checklist"],
                content=(
                    "| Maintenance Task | Interval/Frequency | Component | Notes |\n"
                    "| --- | --- | --- | --- |\n"
                    "| Inspect intake air filter | as required | - | X |"
                ),
            )
        ],
    )

    assert len(context.maintenance_entries) == 1
    entry = context.maintenance_entries[0]
    assert entry.task == "Inspect intake air filter"
    assert entry.interval == "as required"
    assert entry.component == "intake air filter"
    assert entry.notes is None
    assert entry.description == "Inspect intake air filter"
