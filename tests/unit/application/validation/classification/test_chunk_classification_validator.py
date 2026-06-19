from src.application.validation.classification import ChunkClassificationValidator


def test_chunk_classification_validator_accepts_valid_classification(
    sample_chunk_classification,
) -> None:
    result = ChunkClassificationValidator().validate(
        sample_chunk_classification
    )

    assert result.is_valid


def test_chunk_classification_validator_requires_chunk_id(
    sample_chunk_classification,
) -> None:
    sample_chunk_classification.chunk_id = ""

    result = ChunkClassificationValidator().validate(
        sample_chunk_classification
    )

    assert not result.is_valid
    assert result.issues[0].code == "classification.chunk_id.required"


def test_chunk_classification_validator_requires_document_id(
    sample_chunk_classification,
) -> None:
    sample_chunk_classification.document_id = ""

    result = ChunkClassificationValidator().validate(
        sample_chunk_classification
    )

    assert not result.is_valid
    assert result.issues[0].code == "classification.document_id.required"


def test_chunk_classification_validator_requires_result(
    sample_chunk_classification,
) -> None:
    sample_chunk_classification.result = None

    result = ChunkClassificationValidator().validate(
        sample_chunk_classification
    )

    assert not result.is_valid
    assert result.issues[0].code == "classification.result.required"


def test_chunk_classification_validator_rejects_invalid_confidence(
    sample_chunk_classification,
) -> None:
    sample_chunk_classification.result.confidence_score = -0.1

    result = ChunkClassificationValidator().validate(
        sample_chunk_classification
    )

    assert not result.is_valid
    assert result.issues[0].code == "classification.confidence.invalid"