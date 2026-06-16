from domain.classification import ClassificationResult


def test_classification_result_is_confident() -> None:
    result = ClassificationResult(
        classification_id="class_001",
        document_id="doc_001",
        predicted_label="manual",
        confidence_score=0.9,
    )

    assert result.is_confident(0.75)


def test_classification_result_is_not_confident_without_score() -> None:
    result = ClassificationResult(
        classification_id="class_001",
        document_id="doc_001",
        predicted_label="manual",
    )

    assert not result.is_confident(0.75)