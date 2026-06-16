import pytest

from src.domain.assets import PictureAsset, TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import (
    ChunkType,
    DocumentType,
    ElementType,
    IdentifierType,
    SourceLocation,
)
from src.domain.document import (
    Document,
    DocumentChunk,
    DocumentGraph,
    DocumentHashes,
    DocumentSection,
    GeneratedQuestion,
    Identifier,
)
from src.domain.elements import CanonicalElement
from src.domain.extraction import (
    EquipmentInfo,
    ExtractionResult,
    MaintenanceTask,
    Manufacturer,
    SparePart,
)
from src.domain.retrieval import Citation, RetrievalQuery, RetrievalResult, RetrievedChunk
from src.domain.workflows import IngestionRun


@pytest.fixture
def document_id() -> str:
    return "doc_001"


@pytest.fixture
def section_id() -> str:
    return "sec_001"


@pytest.fixture
def chunk_id() -> str:
    return "chunk_001"


@pytest.fixture
def sample_source_location() -> SourceLocation:
    return SourceLocation(
        page_start=10,
        page_end=10,
    )


@pytest.fixture
def sample_document(document_id: str) -> Document:
    return Document(
        document_id=document_id,
        file_name="pump_manual.pdf",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        title="Hydraulic Pump Manual",
        document_type=DocumentType.MANUAL,
    )


@pytest.fixture
def sample_section(
    document_id: str,
    section_id: str,
    sample_source_location: SourceLocation,
) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id=document_id,
        title="Maintenance Schedule",
        level=1,
        section_path=["Maintenance Schedule"],
        source=sample_source_location,
        element_ids=["el_001"],
        sequence_number=1,
    )


@pytest.fixture
def sample_element(
    document_id: str,
    section_id: str,
    sample_source_location: SourceLocation,
) -> CanonicalElement:
    return CanonicalElement(
        element_id="el_001",
        document_id=document_id,
        element_type=ElementType.TEXT,
        text="Replace hydraulic filter every 1000 operating hours.",
        parent_section_id=section_id,
        reading_order=1,
        source=sample_source_location,
    )


@pytest.fixture
def sample_chunk(
    document_id: str,
    section_id: str,
    chunk_id: str,
    sample_source_location: SourceLocation,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        section_id=section_id,
        content="Replace hydraulic filter every 1000 operating hours.",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["Maintenance Schedule"],
        element_ids=["el_001"],
        source=sample_source_location,
    )


@pytest.fixture
def sample_identifier(
    document_id: str,
    chunk_id: str,
) -> Identifier:
    return Identifier(
        identifier_id="identifier_001",
        document_id=document_id,
        chunk_id=chunk_id,
        raw_value=" HP-001 ",
        identifier_type=IdentifierType.PART_NUMBER,
    )


@pytest.fixture
def sample_question(
    document_id: str,
    chunk_id: str,
) -> GeneratedQuestion:
    return GeneratedQuestion(
        question_id="question_001",
        document_id=document_id,
        chunk_id=chunk_id,
        question="When should the hydraulic filter be replaced?",
    )


@pytest.fixture
def sample_table_asset(document_id: str, section_id: str) -> TableAsset:
    return TableAsset(
        table_id="table_001",
        document_id=document_id,
        parent_section_id=section_id,
        markdown="| Part Number | Description |\n|---|---|\n| HP-001 | Filter |",
        metadata=AssetMetadata(
            caption="Spare parts table",
            nearby_text="The following table lists spare parts.",
        ),
    )


@pytest.fixture
def sample_picture_asset(document_id: str, section_id: str) -> PictureAsset:
    return PictureAsset(
        picture_id="pic_001",
        document_id=document_id,
        parent_section_id=section_id,
        image_path="outputs/images/pic_001.png",
        ocr_text="FILTER HOUSING HP-001",
        ocr_confidence=0.95,
        metadata=AssetMetadata(
            caption="Exploded view of hydraulic pump",
            nearby_text="Figure shows the hydraulic pump assembly.",
        ),
    )


@pytest.fixture
def sample_document_graph(
    sample_document: Document,
    sample_section: DocumentSection,
    sample_element: CanonicalElement,
    sample_chunk: DocumentChunk,
    sample_identifier: Identifier,
    sample_question: GeneratedQuestion,
    sample_table_asset: TableAsset,
    sample_picture_asset: PictureAsset,
) -> DocumentGraph:
    graph = DocumentGraph(document=sample_document)

    graph.add_section(sample_section)
    graph.add_element(sample_element)
    graph.add_chunk(sample_chunk)

    graph.identifiers[sample_identifier.identifier_id] = sample_identifier
    graph.questions[sample_question.question_id] = sample_question
    graph.tables[sample_table_asset.table_id] = sample_table_asset
    graph.pictures[sample_picture_asset.picture_id] = sample_picture_asset

    return graph


@pytest.fixture
def sample_maintenance_task(document_id: str, chunk_id: str) -> MaintenanceTask:
    return MaintenanceTask(
        task_id="task_001",
        document_id=document_id,
        title="Replace hydraulic filter",
        interval="1000 operating hours",
        component_name="Hydraulic filter",
        source_chunk_id=chunk_id,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_spare_part(document_id: str, chunk_id: str) -> SparePart:
    return SparePart(
        spare_part_id="spare_001",
        document_id=document_id,
        part_number="HP-001",
        description="Hydraulic filter",
        quantity="1",
        source_chunk_id=chunk_id,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_equipment_info(document_id: str, chunk_id: str) -> EquipmentInfo:
    return EquipmentInfo(
        equipment_id="equipment_001",
        document_id=document_id,
        name="Hydraulic Pump",
        model_number="HP-500",
        manufacturer_name="Example Manufacturer",
        source_chunk_id=chunk_id,
        confidence_score=0.85,
    )


@pytest.fixture
def sample_manufacturer(document_id: str, chunk_id: str) -> Manufacturer:
    return Manufacturer(
        manufacturer_id="manufacturer_001",
        document_id=document_id,
        name="Example Manufacturer",
        source_chunk_id=chunk_id,
        confidence_score=0.85,
    )


@pytest.fixture
def sample_extraction_result(
    document_id: str,
    sample_maintenance_task: MaintenanceTask,
    sample_spare_part: SparePart,
    sample_equipment_info: EquipmentInfo,
    sample_manufacturer: Manufacturer,
) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_001",
        document_id=document_id,
        maintenance_tasks=[sample_maintenance_task],
        spare_parts=[sample_spare_part],
        equipment=[sample_equipment_info],
        manufacturers=[sample_manufacturer],
        confidence_score=0.88,
    )


@pytest.fixture
def sample_retrieval_query() -> RetrievalQuery:
    return RetrievalQuery(
        query_id="query_001",
        query_text="When should the hydraulic filter be replaced?",
        document_types=[DocumentType.MANUAL],
        chunk_types=[ChunkType.MAINTENANCE_INTERVAL],
        top_k=5,
    )


@pytest.fixture
def sample_citation(
    document_id: str,
    section_id: str,
    chunk_id: str,
    sample_source_location: SourceLocation,
) -> Citation:
    return Citation(
        citation_id="citation_001",
        document_id=document_id,
        chunk_id=chunk_id,
        section_id=section_id,
        document_name="pump_manual.pdf",
        section_title="Maintenance Schedule",
        source=sample_source_location,
    )


@pytest.fixture
def sample_retrieved_chunk(
    document_id: str,
    section_id: str,
    chunk_id: str,
    sample_citation: Citation,
    sample_source_location: SourceLocation,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content="Replace hydraulic filter every 1000 operating hours.",
        score=0.91,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_id=section_id,
        section_path=["Maintenance Schedule"],
        source=sample_source_location,
        citation=sample_citation,
    )


@pytest.fixture
def sample_retrieval_result(
    sample_retrieval_query: RetrievalQuery,
    sample_retrieved_chunk: RetrievedChunk,
    sample_citation: Citation,
) -> RetrievalResult:
    return RetrievalResult(
        result_id="retrieval_result_001",
        query=sample_retrieval_query,
        chunks=[sample_retrieved_chunk],
        citations=[sample_citation],
        used_dense=True,
        total_candidates=1,
    )


@pytest.fixture
def sample_ingestion_run() -> IngestionRun:
    return IngestionRun(
        run_id="run_001",
        file_path="data/input/pump_manual.pdf",
        file_hash="file_hash_001",
    )