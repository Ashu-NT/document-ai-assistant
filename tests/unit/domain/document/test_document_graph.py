def test_document_graph_returns_section_elements(sample_document_graph) -> None:
    elements = sample_document_graph.get_section_elements("sec_001")

    assert len(elements) == 1
    assert elements[0].element_id == "el_001"


def test_document_graph_returns_chunk_questions(sample_document_graph) -> None:
    questions = sample_document_graph.get_chunk_questions("chunk_001")

    assert len(questions) == 1
    assert questions[0].question_id == "question_001"


def test_document_graph_returns_chunk_identifiers(sample_document_graph) -> None:
    identifiers = sample_document_graph.get_chunk_identifiers("chunk_001")

    assert len(identifiers) == 1
    assert identifiers[0].identifier_id == "identifier_001"


def test_document_graph_can_add_section(sample_document_graph, sample_section) -> None:
    sample_document_graph.add_section(sample_section)

    assert "sec_001" in sample_document_graph.sections


def test_document_graph_can_add_chunk(sample_document_graph, sample_chunk) -> None:
    sample_document_graph.add_chunk(sample_chunk)

    assert "chunk_001" in sample_document_graph.chunks


def test_document_graph_can_replace_chunks(sample_document_graph, sample_chunk) -> None:
    replacement_chunk = sample_chunk.__class__(
        chunk_id="chunk_002",
        document_id=sample_chunk.document_id,
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

    sample_document_graph.replace_chunks([replacement_chunk])

    assert list(sample_document_graph.chunks) == ["chunk_002"]


def test_document_graph_can_replace_questions(
    sample_document_graph,
    sample_question,
) -> None:
    replacement_question = sample_question.__class__(
        question_id="question_002",
        document_id=sample_question.document_id,
        chunk_id=sample_question.chunk_id,
        question="Updated question?",
        is_active=sample_question.is_active,
        processing_metadata=sample_question.processing_metadata,
    )

    sample_document_graph.replace_questions([replacement_question])

    assert list(sample_document_graph.questions) == ["question_002"]


def test_document_graph_can_clear_chunk_dependents(sample_document_graph) -> None:
    sample_document_graph.clear_chunk_dependents()

    assert sample_document_graph.questions == {}
    assert sample_document_graph.identifiers == {}
