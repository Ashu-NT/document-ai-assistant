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