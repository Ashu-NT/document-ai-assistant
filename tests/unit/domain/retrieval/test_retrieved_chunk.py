def test_retrieved_chunk_relevance(sample_retrieved_chunk) -> None:
    assert sample_retrieved_chunk.is_relevant(0.55)


def test_retrieved_chunk_section_path_text(sample_retrieved_chunk) -> None:
    assert sample_retrieved_chunk.section_path_text() == "Maintenance Schedule"