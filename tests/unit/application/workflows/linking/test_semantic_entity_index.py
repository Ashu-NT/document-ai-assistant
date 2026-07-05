from src.application.workflows.linking.semantic_entity_index import (
    IndexedEntity,
    SemanticEntityIndex,
)
from src.domain.extraction import SemanticEntityType, SemanticSourceMetadata


def test_from_source_metadata_returns_none_when_metadata_missing() -> None:
    indexed = IndexedEntity.from_source_metadata(
        SemanticEntityType.MAINTENANCE_TASK, "task_001", None
    )

    assert indexed is None


def test_from_source_metadata_copies_locality_fields() -> None:
    metadata = SemanticSourceMetadata(
        document_id="document_001",
        chunk_id="chunk_001",
        section_id="section_001",
        parent_section_id="section_root",
        table_id="table_001",
        page_start=3,
        nearby_chunk_ids=("chunk_000", "chunk_002"),
    )

    indexed = IndexedEntity.from_source_metadata(
        SemanticEntityType.PROCEDURE, "procedure_001", metadata
    )

    assert indexed is not None
    assert indexed.entity_type == SemanticEntityType.PROCEDURE
    assert indexed.entity_id == "procedure_001"
    assert indexed.chunk_id == "chunk_001"
    assert indexed.section_id == "section_001"
    assert indexed.parent_section_id == "section_root"
    assert indexed.table_id == "table_001"
    assert indexed.page_start == 3
    assert indexed.nearby_chunk_ids == ("chunk_000", "chunk_002")


def _entity(entity_type, entity_id, **overrides) -> IndexedEntity:
    defaults = {
        "chunk_id": None,
        "section_id": None,
        "parent_section_id": None,
        "table_id": None,
        "page_start": None,
        "nearby_chunk_ids": (),
    }
    defaults.update(overrides)
    return IndexedEntity(entity_type=entity_type, entity_id=entity_id, **defaults)


def test_buckets_entities_by_locality_signal() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        chunk_id="chunk_001",
        section_id="section_001",
        parent_section_id="section_root",
        table_id="table_001",
        page_start=2,
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        chunk_id="chunk_001",
        section_id="section_001",
        parent_section_id="section_root",
        table_id="table_001",
        page_start=2,
    )
    unrelated = _entity(SemanticEntityType.SPARE_PART, "spare_001")

    index = SemanticEntityIndex([task, procedure, unrelated])

    assert index.by_chunk["chunk_001"] == [task, procedure]
    assert index.by_section["section_001"] == [task, procedure]
    assert index.by_parent_section["section_root"] == [task, procedure]
    assert index.by_table["table_001"] == [task, procedure]
    assert index.sorted_by_page == [task, procedure]


def test_entities_without_locality_signals_are_not_bucketed() -> None:
    entity = _entity(SemanticEntityType.SPARE_PART, "spare_001")

    index = SemanticEntityIndex([entity])

    assert index.by_chunk == {}
    assert index.by_section == {}
    assert index.by_parent_section == {}
    assert index.by_table == {}
    assert index.sorted_by_page == []


def test_sorted_by_page_orders_ascending() -> None:
    a = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_001", page_start=5)
    b = _entity(SemanticEntityType.PROCEDURE, "procedure_001", page_start=1)
    c = _entity(SemanticEntityType.SPARE_PART, "spare_001", page_start=3)

    index = SemanticEntityIndex([a, b, c])

    assert [entity.entity_id for entity in index.sorted_by_page] == [
        "procedure_001",
        "spare_001",
        "task_001",
    ]
