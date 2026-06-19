from src.application.validation.classification import (
    DocumentClassificationValidator,
)


def test_document_classification_validator_accepts_valid_classification(
    sample_document_classification,
) -> None:
    result = DocumentClassificationValidator().validate(
        sample_document_classification
    )

    assert result.is_valid


def test_document_classification_validator_requires_document_id(
    sample_document_classification,
) -> None:
    sample_document_classification.document_id = ""

    result = DocumentClassificationValidator().validate(
        sample_document_classification
    )

    assert not result.is_valid
    assert result.issues[0].code == "classification.document_id.required"


def test_document_classification_validator_requires_result(
    sample_document_classification,
) -> None:
    sample_document_classification.result = None

    result = DocumentClassificationValidator().validate(
        sample_document_classification
    )

    assert not result.is_valid
    assert result.issues[0].code == "classification.result.required"


def test_document_classification_validator_rejects_invalid_confidence(
    sample_document_classification,
) -> None:
    sample_document_classification.result.confidence_score = 1.5

    result = DocumentClassificationValidator().validate(
        sample_document_classification
    )

    assert not result.is_valid
    assert result.issues[0].code == "classification.confidence.invalid"