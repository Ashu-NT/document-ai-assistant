def test_retrieval_query_uses_original_query_when_not_rewritten(
    sample_retrieval_query,
) -> None:
    assert sample_retrieval_query.effective_query() == sample_retrieval_query.query_text


def test_retrieval_query_uses_rewritten_query() -> None:
    from domain.retrieval import RetrievalQuery

    query = RetrievalQuery(
        query_id="query_001",
        query_text="part no HP-001",
        rewritten_query="part number HP-001",
    )

    assert query.effective_query() == "part number HP-001"


def test_retrieval_query_detects_identifiers() -> None:
    from domain.retrieval import RetrievalQuery

    query = RetrievalQuery(
        query_id="query_001",
        query_text="Find HP-001",
        detected_identifiers=["HP-001"],
    )

    assert query.has_identifiers()