from __future__ import annotations

from src.application.validation.ingestion import IngestionRequestValidator
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest


def test_validate_flags_file_too_large_when_explicit_limit_is_exceeded(
    tmp_path,
) -> None:
    input_file = tmp_path / "oversized.pdf"
    input_file.write_bytes(b"%PDF-1.7\n0123456789")
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
    input_file.write_bytes(b"%PDF-1.7\n0123456789")
    validator = IngestionRequestValidator()

    result = validator.validate(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert result.is_valid is True


def test_validate_flags_content_mismatch_when_pdf_extension_but_wrong_signature(
    tmp_path,
) -> None:
    input_file = tmp_path / "fake.pdf"
    input_file.write_bytes(b"not actually a pdf")
    validator = IngestionRequestValidator()

    result = validator.validate(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert result.is_valid is False
    assert any(
        issue.code == "ingestion.file_path.content_mismatch"
        for issue in result.issues
    )


def test_validate_does_not_double_flag_content_mismatch_for_unsupported_extension(
    tmp_path,
) -> None:
    input_file = tmp_path / "not_a_pdf.docx"
    input_file.write_bytes(b"not actually a pdf")
    validator = IngestionRequestValidator()

    result = validator.validate(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert result.is_valid is False
    codes = [issue.code for issue in result.issues]
    assert codes.count("ingestion.file_path.unsupported_extension") == 1
    assert "ingestion.file_path.content_mismatch" not in codes
