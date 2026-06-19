from src.application.validation.extraction import (
    ExtractionResultValidator,
)


def test_extraction_result_validator_accepts_valid_result(
    sample_extraction_result,
) -> None:
    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert result.is_valid


def test_extraction_result_validator_requires_extraction_id(
    sample_extraction_result,
) -> None:
    sample_extraction_result.extraction_id = ""

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert result.issues[0].code == "extraction.id.required"


def test_extraction_result_validator_requires_document_id(
    sample_extraction_result,
) -> None:
    sample_extraction_result.document_id = ""

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert result.issues[0].code == "extraction.document_id.required"


def test_extraction_result_validator_rejects_invalid_confidence(
    sample_extraction_result,
) -> None:
    sample_extraction_result.confidence_score = 1.5

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert result.issues[0].code == "extraction.confidence.invalid"


def test_extraction_result_validator_detects_maintenance_task_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.maintenance_tasks[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.task.document_mismatch"
    )


def test_extraction_result_validator_detects_spare_part_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.spare_parts[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.spare_part.document_mismatch"
    )


def test_extraction_result_validator_detects_equipment_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.equipment[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.equipment.document_mismatch"
    )


def test_extraction_result_validator_detects_manufacturer_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.manufacturers[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.manufacturer.document_mismatch"
    )