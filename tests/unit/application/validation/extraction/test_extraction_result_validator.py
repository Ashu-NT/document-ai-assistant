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


def test_extraction_result_validator_detects_supplier_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.suppliers[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.supplier.document_mismatch"
    )


def test_extraction_result_validator_detects_procedure_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.procedures[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.procedure.document_mismatch"
    )


def test_extraction_result_validator_detects_specification_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.specifications[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.specification.document_mismatch"
    )


def test_extraction_result_validator_detects_safety_warning_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.safety_warnings[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.safety_warning.document_mismatch"
    )


def test_extraction_result_validator_detects_maintenance_interval_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.maintenance_intervals[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.maintenance_interval.document_mismatch"
    )


def test_extraction_result_validator_detects_troubleshooting_entry_document_mismatch(
    sample_extraction_result,
) -> None:
    sample_extraction_result.troubleshooting_entries[0].document_id = "wrong_doc"

    result = ExtractionResultValidator().validate(
        sample_extraction_result
    )

    assert not result.is_valid
    assert (
        result.issues[0].code
        == "extraction.troubleshooting_entry.document_mismatch"
    )