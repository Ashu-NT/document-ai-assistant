def test_retrieval_query_uses_original_query_when_not_rewritten(
    sample_retrieval_query,
) -> None:
    assert sample_retrieval_query.effective_query() == sample_retrieval_query.query_text


def test_retrieval_query_uses_rewritten_query() -> None:
    from src.domain.retrieval import RetrievalQuery

    query = RetrievalQuery(
        query_id="query_001",
        query_text="part no HP-001",
        rewritten_query="part number HP-001",
    )

    assert query.effective_query() == "part number HP-001"


def test_retrieval_query_detects_identifiers() -> None:
    from src.domain.retrieval import RetrievalQuery

    query = RetrievalQuery(
        query_id="query_001",
        query_text="Find HP-001",
        detected_identifiers=["HP-001"],
    )

    assert query.has_identifiers()


def test_retrieval_query_intent_classification_fields_default_to_none() -> None:
    """Before RetrievalQueryAnalyzer.analyze() has run, the classification
    fields must be inert -- these are new, optional fields (PR 1,
    answering_flow_weakness_remediation_plan.md), not a required part of
    constructing a RetrievalQuery."""
    from src.domain.retrieval import RetrievalQuery

    query = RetrievalQuery(query_id="query_001", query_text="Find HP-001")

    assert query.intent_best_score is None
    assert query.intent_runner_up_score is None
    assert query.intent_score_gap is None
    assert query.intent_confidence is None
    assert query.intent_runner_up is None