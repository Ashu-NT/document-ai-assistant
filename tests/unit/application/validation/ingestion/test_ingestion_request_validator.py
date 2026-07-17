from __future__ import annotations

from src.application.validation.ingestion import IngestionRequestValidator
from src.application.workflows.ingestion.ingestion_request import IngestionRequest


def test_validate_flags_file_too_large_when_explicit_limit_is_exceeded(
    tmp_path,
) -> None:
    input_file = tmp_path / "oversized.pdf"
    input_file.write_bytes(b"0123456789")
    validator = IngestionRequestValidator(max_file_size_bytes=4)

    result = validator.validate(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert result.is_valid is False
    assert any(
        issue.code == "ingestion.file_path.file_too_large"
        for issue in result.issues
    )


def test_validate_skips_size_check_when_no_explicit_limit_is_configured(
    tmp_path,
) -> None:
    input_file = tmp_path / "allowed.pdf"
    input_file.write_bytes(b"0123456789")
    validator = IngestionRequestValidator()

    result = validator.validate(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert result.is_valid is True
