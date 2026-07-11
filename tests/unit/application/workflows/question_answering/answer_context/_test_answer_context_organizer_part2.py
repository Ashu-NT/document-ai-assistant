from src.application.services.answer_generation import AnswerIntent

from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
    AnswerKeyValue,
    AnswerSource,
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

class _StubStructuredSourceBuilder:
    def __init__(self, sources: list[AnswerSource]) -> None:
        self.sources = sources
        self.calls: list[list[RetrievedChunk]] = []

    def build_sources(self, chunks) -> list[AnswerSource]:
        self.calls.append(list(chunks))
        return self.sources

class _StubSourceGroupBuilder:
    def __init__(self, result) -> None:
        self.result = result
        self.calls: list[list[AnswerSource]] = []

    def build(self, sources):
        self.calls.append(list(sources))
        return self.result

class _StubSectionGroupBuilder:
    def __init__(self, result) -> None:
        self.result = result
        self.calls: list[list[AnswerSource]] = []

    def build(self, sources):
        self.calls.append(list(sources))
        return self.result

class _StubKeyValueExtractor:
    def __init__(self, key_values) -> None:
        self.key_values = key_values
        self.extract_calls: list[tuple[list[AnswerSource], AnswerIntent]] = []

    def extract(self, sources, *, answer_intent):
        self.extract_calls.append((list(sources), answer_intent))
        return self.key_values

class _StubMaintenanceTaskExtractor:
    def __init__(self, maintenance_entries) -> None:
        self.maintenance_entries = maintenance_entries
        self.extract_maintenance_calls: list[tuple[list[AnswerSource], AnswerIntent]] = []

    def extract_maintenance_entries(self, sources, *, answer_intent):
        self.extract_maintenance_calls.append((list(sources), answer_intent))
        return self.maintenance_entries

class _StubMaintenanceEntryMerger:
    def __init__(self, merged_entries) -> None:
        self.merged_entries = merged_entries
        self.calls = []

    def merge(self, entries):
        self.calls.append(list(entries))
        return self.merged_entries

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
