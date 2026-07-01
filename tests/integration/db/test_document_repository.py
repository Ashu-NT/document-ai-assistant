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


def test_document_repository_replaces_document_graph(
    db_uow,
    sample_document_graph,
    sample_document,
    sample_source_location,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    updated_graph = copy.deepcopy(sample_document_graph)
    updated_section = updated_graph.sections.pop("sec_001")
    updated_section.section_id = "sec_002"
    updated_section.title = "Updated Maintenance Procedure"
    updated_section.section_path = ["Updated Maintenance Procedure"]
    updated_section.element_ids = ["el_002"]
    updated_graph.sections = {updated_section.section_id: updated_section}

    updated_element = updated_graph.elements.pop("el_001")
    updated_element.element_id = "el_002"
    updated_element.text = "Inspect drive belt tension every 250 operating hours."
    updated_element.parent_section_id = updated_section.section_id
    updated_element.source = sample_source_location
    updated_graph.elements = {updated_element.element_id: updated_element}

    updated_chunk = next(iter(updated_graph.chunks.values()))
    updated_graph.chunks = {}
    updated_chunk.chunk_id = "chunk_002"
    updated_chunk.section_id = updated_section.section_id
    updated_chunk.content = "Inspect drive belt tension every 250 operating hours."
    updated_chunk.section_path = ["Updated Maintenance Procedure"]
    updated_chunk.element_ids = [updated_element.element_id]
    updated_graph.add_chunk(updated_chunk)

    updated_question = next(iter(updated_graph.questions.values()))
    updated_question.question_id = "question_002"
    updated_question.chunk_id = updated_chunk.chunk_id
    updated_question.question = "When should the drive belt tension be inspected?"
    updated_graph.questions = {updated_question.question_id: updated_question}

    updated_identifier = next(iter(updated_graph.identifiers.values()))
    updated_identifier.identifier_id = "identifier_002"
    updated_identifier.chunk_id = updated_chunk.chunk_id
    updated_identifier.raw_value = " DB-250 "
    updated_graph.identifiers = {
        updated_identifier.identifier_id: updated_identifier
    }

    updated_graph.document.title = "Updated Document"
    updated_graph.document.file_name = sample_document.file_name
    updated_graph.document.file_path = sample_document.file_path

    db_uow.documents.replace_document_graph(updated_graph)
    db_uow.commit()

    loaded = db_uow.documents.get_document_graph(document_id)

    assert loaded is not None
    assert list(loaded.sections) == ["sec_002"]
    assert list(loaded.elements) == ["el_002"]
    assert list(loaded.chunks) == ["chunk_002"]
    assert list(loaded.questions) == ["question_002"]
    assert list(loaded.identifiers) == ["identifier_002"]
