from src.infrastructure.db.mappers import ChunkMapper


def test_chunk_mapper_round_trip(sample_chunk) -> None:
    sample_chunk.element_ids = ["el_001", "el_002"]
    sample_chunk.table_ids = ["table_001"]
    sample_chunk.picture_ids = ["pic_001"]
    sample_chunk.logical_table_family_id = "table_family_001"
    sample_chunk.logical_table_family_index = 1
    sample_chunk.logical_table_family_total = 2
    sample_chunk.logical_table_continuation_role = "start"
    sample_chunk.table_category = "maintenance_interval_table"
    sample_chunk.table_category_confidence = 0.94
    sample_chunk.table_row_start = 1
    sample_chunk.table_row_end = 12
    orm = ChunkMapper.to_orm(sample_chunk)
    domain = ChunkMapper.to_domain(orm)

    assert domain.chunk_id == sample_chunk.chunk_id
    assert domain.document_id == sample_chunk.document_id
    assert domain.content == sample_chunk.content
    assert domain.chunk_type == sample_chunk.chunk_type
    assert domain.section_path == sample_chunk.section_path
    assert domain.element_ids == sample_chunk.element_ids
    assert domain.table_ids == sample_chunk.table_ids
    assert domain.picture_ids == sample_chunk.picture_ids
    assert domain.logical_table_family_id == "table_family_001"
    assert domain.logical_table_family_index == 1
    assert domain.logical_table_family_total == 2
    assert domain.logical_table_continuation_role == "start"
    assert domain.table_category == "maintenance_interval_table"
    assert domain.table_category_confidence == 0.94
    assert domain.table_row_start == 1
    assert domain.table_row_end == 12
    assert orm.element_ids_json == '["el_001", "el_002"]'
    assert orm.table_ids_json == '["table_001"]'
    assert orm.picture_ids_json == '["pic_001"]'
