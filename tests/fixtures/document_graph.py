import pytest

from src.domain.assets import FormAsset, PictureAsset, TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.assets.form_field import FormField
from src.domain.common import ChunkType, DocumentType, ElementType, IdentifierType
from src.domain.common.source_location import SourceLocation
from src.domain.document import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    Document,
    DocumentChunk,
    DocumentGraph,
    DocumentHashes,
    DocumentSection,
    GeneratedQuestion,
    Identifier,
)
from src.domain.elements import CanonicalElement


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
    return SourceLocation(page_start=10, page_end=10)


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
def sample_identifier(document_id: str, chunk_id: str) -> Identifier:
    return Identifier(
        identifier_id="identifier_001",
        document_id=document_id,
        chunk_id=chunk_id,
        raw_value=" HP-001 ",
        identifier_type=IdentifierType.PART_NUMBER,
    )


@pytest.fixture
def sample_chunk_cross_reference(document_id: str, chunk_id: str) -> ChunkCrossReference:
    return ChunkCrossReference(
        cross_reference_id="xref_001",
        document_id=document_id,
        source_chunk_id=chunk_id,
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        matched_text="(→ Page 42)",
        target_page=42,
        target_chunk_id="chunk_002",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_question(document_id: str, chunk_id: str) -> GeneratedQuestion:
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
def sample_form_asset(document_id: str, section_id: str) -> FormAsset:
    return FormAsset(
        form_id="form_001",
        document_id=document_id,
        parent_section_id=section_id,
        fields=[
            FormField(
                label="key",
                key_text="Model",
                value_text="HP-001",
                cell_id=0,
            )
        ],
        metadata=AssetMetadata(
            caption="Equipment identification form",
            nearby_text="The following form identifies the equipment.",
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
    sample_form_asset: FormAsset,
) -> DocumentGraph:
    graph = DocumentGraph(document=sample_document)
    graph.add_section(sample_section)
    graph.add_element(sample_element)
    graph.add_chunk(sample_chunk)
    graph.identifiers[sample_identifier.identifier_id] = sample_identifier
    graph.questions[sample_question.question_id] = sample_question
    graph.tables[sample_table_asset.table_id] = sample_table_asset
    graph.pictures[sample_picture_asset.picture_id] = sample_picture_asset
    graph.forms[sample_form_asset.form_id] = sample_form_asset
    return graph
