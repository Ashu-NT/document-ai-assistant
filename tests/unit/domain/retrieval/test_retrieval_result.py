def test_retrieval_result_has_results(sample_retrieval_result) -> None:
    assert sample_retrieval_result.has_results()


def test_retrieval_result_returns_best_score(sample_retrieval_result) -> None:
    assert sample_retrieval_result.best_score() == 0.91


def test_retrieval_result_has_enough_evidence(sample_retrieval_result) -> None:
    assert sample_retrieval_result.has_enough_evidence(min_chunks=1)


def test_retrieval_result_top_chunks(sample_retrieval_result) -> None:
    top_chunks = sample_retrieval_result.top_chunks(limit=1)

    assert len(top_chunks) == 1
    assert top_chunks[0].chunk_id == "chunk_001"