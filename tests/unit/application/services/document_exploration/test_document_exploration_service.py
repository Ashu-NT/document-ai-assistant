"""
Tests for DocumentExplorationService.

The service reads exclusively from DocumentGraph — no Qdrant, no embeddings,
no LLM calls. Tests use a FakeDocumentRepository backed by in-memory data;
the absence of any mock/patch for external services proves the service never
reaches them.
"""
import pytest

from src.application.services.document import DocumentLookupService
from src.application.services.document_exploration import (
    DocumentExplorationService,
    DocumentNotFoundError,
)
from src.domain.common import ChunkType
from src.domain.document import Document, DocumentChunk, DocumentGraph, DocumentSection
from src.domain.document.value_objects import DocumentStatistics


# ---------------------------------------------------------------------------
# Fake repository — in-memory only, no external dependencies
# ---------------------------------------------------------------------------

class FakeDocumentRepository:
    def __init__(self) -> None:
        self.graphs: dict[str, DocumentGraph] = {}

    def get_document_graph(self, document_id: str) -> DocumentGraph | None:
        return self.graphs.get(document_id)

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list:
        return []

    def list_chunks_by_document(self, document_id: str) -> list:
        return []

    def search_identifiers(self, value: str) -> list:
        return []


@pytest.fixture
def fake_repository() -> FakeDocumentRepository:
    return FakeDocumentRepository()


@pytest.fixture
def lookup_service(fake_repository: FakeDocumentRepository) -> DocumentLookupService:
    return DocumentLookupService(fake_repository)


@pytest.fixture
def service(lookup_service: DocumentLookupService) -> DocumentExplorationService:
    return DocumentExplorationService(lookup_service)


# ---------------------------------------------------------------------------
# Item 7 — explore_graph() returns all expected projections
# ---------------------------------------------------------------------------

def test_explore_graph_returns_overview(
    service: DocumentExplorationService,
    sample_document_graph: DocumentGraph,
    document_id: str,
) -> None:
    result = service.explore_graph(sample_document_graph)

    assert result.overview is not None
    assert result.overview.document_id == document_id
    assert result.overview.title == "Hydraulic Pump Manual"
    assert result.overview.file_name == "pump_manual.pdf"
    assert result.overview.document_type == "manual"


def test_explore_graph_returns_sections(
    service: DocumentExplorationService,
    sample_document_graph: DocumentGraph,
) -> None:
    result = service.explore_graph(sample_document_graph)

    assert result.sections is not None
    assert len(result.sections) == 1
    assert result.sections[0].title == "Maintenance Schedule"
    assert result.sections[0].level == 1
    assert result.sections[0].section_path == ["Maintenance Schedule"]


def test_explore_graph_returns_identifiers(
    service: DocumentExplorationService,
    sample_document_graph: DocumentGraph,
) -> None:
    result = service.explore_graph(sample_document_graph)

    assert result.identifiers is not None
    assert len(result.identifiers) == 1
    identifier = result.identifiers[0]
    assert identifier.identifier_type == "part_number"
    assert identifier.normalized_value == "HP-001"


def test_explore_graph_returns_tables(
    service: DocumentExplorationService,
    sample_document_graph: DocumentGraph,
) -> None:
    result = service.explore_graph(sample_document_graph)

    assert result.tables is not None
    assert len(result.tables) == 1
    table = result.tables[0]
    assert table.table_id == "table_001"
    assert table.caption == "Spare parts table"
    assert table.section_title == "Maintenance Schedule"


def test_explore_graph_returns_assets(
    service: DocumentExplorationService,
    sample_document_graph: DocumentGraph,
) -> None:
    result = service.explore_graph(sample_document_graph)

    assert result.assets is not None
    assert len(result.assets) == 1
    asset = result.assets[0]
    assert asset.picture_id == "pic_001"
    assert asset.caption == "Exploded view of hydraulic pump"
    assert asset.section_title == "Maintenance Schedule"
    assert asset.has_ocr_text is True


def test_explore_graph_returns_coverage(
    service: DocumentExplorationService,
    sample_document_graph_with_stats: DocumentGraph,
) -> None:
    result = service.explore_graph(sample_document_graph_with_stats)

    assert result.coverage is not None
    assert result.coverage.has_sections is True
    assert result.coverage.has_tables is True
    assert result.coverage.has_pictures is True
    assert result.coverage.has_identifiers is True
    assert "maintenance_interval" in result.coverage.chunk_type_counts


# ---------------------------------------------------------------------------
# Item 7 — overview counts fall back to graph collection lengths
#           when DocumentStatistics fields are zero (default fixture state)
# ---------------------------------------------------------------------------

def test_overview_counts_reflect_graph_collections(
    service: DocumentExplorationService,
    sample_document_graph_with_stats: DocumentGraph,
) -> None:
    result = service.explore_graph(sample_document_graph_with_stats)

    assert result.overview.section_count == 1
    assert result.overview.chunk_count == 1
    assert result.overview.table_count == 1
    assert result.overview.picture_count == 1
    assert result.overview.identifier_count == 1


# ---------------------------------------------------------------------------
# Item 7 — sections are ordered by sequence_number
# ---------------------------------------------------------------------------

def test_sections_ordered_by_sequence_number(
    service: DocumentExplorationService,
    sample_document_graph_multi_section: DocumentGraph,
) -> None:
    # Fixture inserts Troubleshooting(3), Installation(1), Maintenance(2) — out of order
    result = service.explore_graph(sample_document_graph_multi_section)

    titles = [s.title for s in result.sections]
    assert titles == ["Installation", "Maintenance", "Troubleshooting"]


# ---------------------------------------------------------------------------
# Item 8 — service is graph-based only (no external calls)
#           Demonstrated by: FakeDocumentRepository has no Qdrant / LLM /
#           embedding logic yet all projections are populated correctly.
# ---------------------------------------------------------------------------

def test_service_uses_no_external_dependencies(
    service: DocumentExplorationService,
    sample_document_graph: DocumentGraph,
    fake_repository: FakeDocumentRepository,
    document_id: str,
) -> None:
    fake_repository.graphs[document_id] = sample_document_graph
    result = service.explore(document_id)
    # If any external call were made it would fail; pure graph projection succeeds
    assert result.document_id == document_id
    assert result.overview is not None


# ---------------------------------------------------------------------------
# Item 9 — explore() raises DocumentNotFoundError for unknown document_id
# ---------------------------------------------------------------------------

def test_explore_raises_for_missing_document(
    service: DocumentExplorationService,
) -> None:
    with pytest.raises(DocumentNotFoundError):
        service.explore("nonexistent_doc_id")


def test_explore_succeeds_when_document_exists(
    service: DocumentExplorationService,
    fake_repository: FakeDocumentRepository,
    sample_document_graph: DocumentGraph,
    document_id: str,
) -> None:
    fake_repository.graphs[document_id] = sample_document_graph
    result = service.explore(document_id)
    assert result.document_id == document_id


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_graph_returns_empty_collections(
    service: DocumentExplorationService,
    sample_document: Document,
) -> None:
    empty_graph = DocumentGraph(document=sample_document)
    result = service.explore_graph(empty_graph)

    assert result.sections == []
    assert result.identifiers == []
    assert result.tables == []
    assert result.assets == []
    assert result.coverage.chunk_type_counts == {}
    assert result.coverage.has_sections is False
    assert result.coverage.has_tables is False
    assert result.coverage.has_pictures is False
    assert result.coverage.has_identifiers is False


# ---------------------------------------------------------------------------
# Exploration metadata — service reads stored fields, no chunk scanning
# ---------------------------------------------------------------------------

def test_sections_expose_overview_text(
    service: DocumentExplorationService,
    sample_document: Document,
) -> None:
    graph = DocumentGraph(document=sample_document)
    section = DocumentSection(
        section_id="sec_001",
        document_id=sample_document.document_id,
        title="Installation",
        level=1,
        overview_text="Section overview: Installation\n\nSubsections: Prerequisites; Steps",
        chunk_type_signals=["installation_instruction"],
    )
    graph.add_section(section)

    result = service.explore_graph(graph)

    entry = result.sections[0]
    assert entry.overview_text == "Section overview: Installation\n\nSubsections: Prerequisites; Steps"
    assert entry.chunk_type_signals == ["installation_instruction"]


def test_sections_expose_chunk_type_signals(
    service: DocumentExplorationService,
    sample_document: Document,
) -> None:
    graph = DocumentGraph(document=sample_document)
    section = DocumentSection(
        section_id="sec_001",
        document_id=sample_document.document_id,
        title="Maintenance",
        level=1,
        chunk_type_signals=["maintenance_interval", "maintenance_procedure"],
    )
    graph.add_section(section)

    result = service.explore_graph(graph)

    assert result.sections[0].chunk_type_signals == ["maintenance_interval", "maintenance_procedure"]


def test_coverage_reads_chunk_type_counts_from_statistics(
    service: DocumentExplorationService,
    sample_document: Document,
) -> None:
    """Service uses statistics.chunk_type_counts, not a live chunk scan."""
    graph = DocumentGraph(document=sample_document)
    # Statistics says 99 technical_specification chunks
    graph.document.statistics = DocumentStatistics(
        chunk_type_counts={"technical_specification": 99},
    )
    # Actual chunk has a DIFFERENT type — proves the service reads from stats
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id=sample_document.document_id,
        section_id=None,
        content="Some content.",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
    )
    graph.add_chunk(chunk)

    result = service.explore_graph(graph)

    assert result.coverage.chunk_type_counts == {"technical_specification": 99}
    assert "maintenance_interval" not in result.coverage.chunk_type_counts


def test_overview_identifier_count_reads_from_statistics(
    service: DocumentExplorationService,
    sample_document: Document,
) -> None:
    """overview.identifier_count reads statistics.identifier_count when set."""
    graph = DocumentGraph(document=sample_document)
    graph.document.statistics = DocumentStatistics(identifier_count=42)

    result = service.explore_graph(graph)

    assert result.overview.identifier_count == 42
