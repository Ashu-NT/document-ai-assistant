import copy

from src.domain.common import ElementType

def test_document_repository_saves_and_loads_document_graph(
    db_uow,
    sample_document_graph,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    loaded = db_uow.documents.get_document_graph(document_id)

    assert loaded is not None
    assert loaded.document.document_id == document_id
    assert len(loaded.sections) == 1
    assert len(loaded.elements) == 1
    assert len(loaded.chunks) == 1
    assert len(loaded.questions) == 1
    assert len(loaded.identifiers) == 1

def test_document_repository_rehydrates_asset_metadata_for_rechunking(
    db_uow,
    sample_document_graph,
    sample_element,
    document_id,
) -> None:
    from src.domain.common import ParserMetadata

    sample_element.table_id = "table_001"
    sample_element.element_type = ElementType.TABLE
    sample_element.parser_metadata = ParserMetadata(
        parser_name="docling",
        raw_source_type="table",
        raw_ref="#/pages/9/elements/1",
        extra={
            "markdown": "| Order Code | Size |\n|---|---|\n| DF-100 | DN100 |",
            "caption": "Ordering information",
            "ocr_text": "DN100 hose connection deck filler",
            "nearby_text": "Use with standard hose connection.",
            "image_path": "outputs/images/deck_filler.png",
            "layout_region_id": "page_9:lane_1",
            "layout_region_role": "body",
            "layout_lane_index": 1,
            "layout_lane_count": 1,
            "page_orientation": "portrait",
        },
    )
    picture_element = sample_element.__class__(
        element_id="el_002",
        document_id=sample_element.document_id,
        element_type=ElementType.PICTURE,
        text=None,
        parent_section_id=sample_element.parent_section_id,
        reading_order=2,
        source=sample_element.source,
        picture_id="pic_001",
        parser_metadata=ParserMetadata(
            parser_name="docling",
            raw_source_type="picture",
            raw_ref="#/pages/9/elements/2",
            extra={
                "caption": "Deck filler dimensions",
                "ocr_text": "DN100 hose connection deck filler",
                "nearby_text": "Use with standard hose connection.",
                "image_path": "outputs/images/deck_filler.png",
            },
        ),
    )
    sample_document_graph.add_element(picture_element)
    sample_document_graph.sections["sec_001"].element_ids.append(picture_element.element_id)
    form_element = sample_element.__class__(
        element_id="el_003",
        document_id=sample_element.document_id,
        element_type=ElementType.FORM,
        text=None,
        parent_section_id=sample_element.parent_section_id,
        reading_order=3,
        source=sample_element.source,
        form_id="form_001",
        parser_metadata=ParserMetadata(
            parser_name="docling",
            raw_source_type="form",
            raw_ref="#/pages/9/elements/3",
            extra={
                "caption": "Equipment identification form",
                "nearby_text": "The following form identifies the equipment.",
                "form_fields": [
                    {
                        "label": "key",
                        "key_text": "Model",
                        "value_text": "HP-001",
                        "cell_id": 0,
                    }
                ],
            },
        ),
    )
    sample_document_graph.add_element(form_element)
    sample_document_graph.sections["sec_001"].element_ids.append(form_element.element_id)
    sample_document_graph.tables["table_001"].markdown = (
        "| Order Code | Size |\n|---|---|\n| DF-100 | DN100 |"
    )
    sample_document_graph.tables["table_001"].metadata.caption = "Ordering information"
    sample_document_graph.pictures["pic_001"].ocr_text = "DN100 hose connection deck filler"
    sample_document_graph.pictures["pic_001"].metadata.caption = "Deck filler dimensions"
    sample_document_graph.pictures["pic_001"].metadata.nearby_text = (
        "Use with standard hose connection."
    )

    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    loaded = db_uow.documents.get_document_graph(document_id)

    assert loaded is not None
    loaded_element = loaded.elements[sample_element.element_id]
    assert loaded_element.parser_metadata is not None
    assert loaded_element.parser_metadata.extra["markdown"].startswith("| Order Code |")
    assert loaded_element.parser_metadata.extra["ocr_text"] == "DN100 hose connection deck filler"
    assert loaded.tables["table_001"].metadata.caption == "Ordering information"
    assert loaded.pictures["pic_001"].metadata.nearby_text == "Use with standard hose connection."
    assert loaded.tables["table_001"].layout_region_id == "page_9:lane_1"
    assert loaded.tables["table_001"].layout_region_role == "body"
    assert loaded.tables["table_001"].layout_lane_index == 1
    assert loaded.tables["table_001"].layout_lane_count == 1
    assert loaded.tables["table_001"].page_orientation == "portrait"
    assert loaded.forms["form_001"].metadata.caption == "Equipment identification form"
    assert (
        loaded.forms["form_001"].metadata.nearby_text
        == "The following form identifies the equipment."
    )
    assert loaded.forms["form_001"].fields[0].key_text == "Model"
    assert loaded.forms["form_001"].fields[0].value_text == "HP-001"
    assert loaded.elements["el_003"].form_id == "form_001"

def test_document_repository_finds_duplicate_by_file_hash(
    db_uow,
    sample_document_graph,
    sample_document,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    found_document_id = db_uow.documents.find_document_id_by_file_hash(
        sample_document.hashes.file_hash,
    )

    assert found_document_id == sample_document.document_id

def test_document_repository_finds_duplicate_by_content_hash(
    db_uow,
    sample_document_graph,
    sample_document,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    found_document_id = db_uow.documents.find_document_id_by_content_hash(
        sample_document.hashes.content_hash,
    )

    assert found_document_id == sample_document.document_id

def test_document_repository_finds_parser_version_by_document_id(
    db_uow,
    sample_document_graph,
    sample_document,
) -> None:
    sample_document_graph.document.parser_version = "docling==2.1.0"
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    found_parser_version = db_uow.documents.find_parser_version_by_document_id(
        sample_document.document_id,
    )

    assert found_parser_version == "docling==2.1.0"

def test_document_repository_returns_none_parser_version_when_not_set(
    db_uow,
    sample_document_graph,
    sample_document,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    found_parser_version = db_uow.documents.find_parser_version_by_document_id(
        sample_document.document_id,
    )

    assert found_parser_version is None

def test_document_repository_lists_chunks_by_document(
    db_uow,
    sample_document_graph,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    chunks = db_uow.documents.list_chunks_by_document(document_id)

    assert len(chunks) == 1
    assert chunks[0].document_id == document_id

def test_document_repository_preserves_chunk_linkage_arrays(
    db_uow,
    sample_document_graph,
    document_id,
) -> None:
    chunk = next(iter(sample_document_graph.chunks.values()))
    chunk.element_ids = ["el_001", "el_002"]
    chunk.table_ids = ["table_001"]
    chunk.picture_ids = ["pic_001"]

    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    loaded_graph = db_uow.documents.get_document_graph(document_id)
    listed_chunks = db_uow.documents.list_chunks_by_document(document_id)

    assert loaded_graph is not None
    loaded_chunk = next(iter(loaded_graph.chunks.values()))
    assert loaded_chunk.element_ids == ["el_001", "el_002"]
    assert loaded_chunk.table_ids == ["table_001"]
    assert loaded_chunk.picture_ids == ["pic_001"]
    assert listed_chunks[0].element_ids == ["el_001", "el_002"]
    assert listed_chunks[0].table_ids == ["table_001"]
    assert listed_chunks[0].picture_ids == ["pic_001"]

def test_document_repository_gets_chunks_by_ids(
    db_uow,
    sample_document_graph,
    chunk_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    chunks = db_uow.documents.get_chunks_by_ids([chunk_id])

    assert len(chunks) == 1
    assert chunks[0].chunk_id == chunk_id

def test_document_repository_searches_identifiers(
    db_uow,
    sample_document_graph,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    identifiers = db_uow.documents.search_identifiers("HP-001")

    assert len(identifiers) == 1
    assert identifiers[0].raw_value.strip() == "HP-001"

def test_document_repository_replaces_document_chunk_artifacts(
    db_uow,
    sample_document_graph,
    sample_chunk,
    sample_question,
    sample_identifier,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    updated_graph = copy.deepcopy(sample_document_graph)
    updated_chunk = sample_chunk.__class__(
        chunk_id="chunk_002",
        document_id=document_id,
        section_id=sample_chunk.section_id,
        content="Updated chunk content.",
        chunk_type=sample_chunk.chunk_type,
        section_path=list(sample_chunk.section_path),
        element_ids=list(sample_chunk.element_ids),
        table_ids=list(sample_chunk.table_ids),
        picture_ids=list(sample_chunk.picture_ids),
        source=sample_chunk.source,
        sequence_number=1,
        chunk_index=1,
        chunk_total=1,
        embedding_text=sample_chunk.embedding_text,
    )
    updated_question = sample_question.__class__(
        question_id="question_002",
        document_id=document_id,
        chunk_id=updated_chunk.chunk_id,
        question="Updated question?",
        is_active=sample_question.is_active,
        processing_metadata=sample_question.processing_metadata,
    )
    updated_identifier = sample_identifier.__class__(
        identifier_id="identifier_002",
        document_id=document_id,
        chunk_id=updated_chunk.chunk_id,
        raw_value=" HP-002 ",
        identifier_type=sample_identifier.identifier_type,
    )

    updated_graph.replace_chunks([updated_chunk])
    updated_graph.replace_questions([updated_question])
    updated_graph.identifiers = {
        updated_identifier.identifier_id: updated_identifier
    }

    db_uow.documents.replace_document_chunk_artifacts(updated_graph)
    db_uow.commit()

    loaded = db_uow.documents.get_document_graph(document_id)

    assert loaded is not None
    assert list(loaded.chunks) == ["chunk_002"]
    assert list(loaded.questions) == ["question_002"]
    assert list(loaded.identifiers) == ["identifier_002"]

def test_document_repository_delete_document_removes_all_dependent_rows(
    db_uow,
    sample_document_graph,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    db_uow.documents.delete_document(document_id)
    db_uow.commit()

    assert db_uow.documents.get_document_graph(document_id) is None
    assert db_uow.documents.get_document_entry(document_id) is None
    assert db_uow.documents.list_chunks_by_document(document_id) == []
    assert db_uow.documents.search_identifiers("HP-001") == []
