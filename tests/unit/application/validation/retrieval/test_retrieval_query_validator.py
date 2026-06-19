from src.application.validation.retrieval import RetrievalQueryValidator


def test_retrieval_query_validator_accepts_valid_query(
    sample_retrieval_query,
) -> None:
    validator = RetrievalQueryValidator()

    result = validator.validate(sample_retrieval_query)

    assert result.is_valid


def test_retrieval_query_validator_rejects_empty_query(
    sample_retrieval_query,
) -> None:
    sample_retrieval_query.query_text = " "

    result = RetrievalQueryValidator().validate(sample_retrieval_query)

    assert not result.is_valid
    assert result.issues[0].code == "retrieval.query.empty"


def test_retrieval_query_validator_rejects_invalid_top_k(
    sample_retrieval_query,
) -> None:
    sample_retrieval_query.top_k = 0

    result = RetrievalQueryValidator().validate(sample_retrieval_query)

    assert not result.is_valid
    assert result.issues[0].code == "retrieval.top_k.invalid"


def test_retrieval_query_validator_requires_one_mode(
    sample_retrieval_query,
) -> None:
    sample_retrieval_query.use_dense = False
    sample_retrieval_query.use_keyword = False
    sample_retrieval_query.use_sql = False

    result = RetrievalQueryValidator().validate(sample_retrieval_query)

    assert not result.is_valid
    assert result.issues[0].code == "retrieval.mode.none_enabled"