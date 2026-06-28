from __future__ import annotations

from pathlib import Path

from src.application.validation.common import ValidationResult, Validator
from src.domain.common import DocumentType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.workflows.ingestion.ingestion_request import (
        IngestionRequest,
     )
_SUPPORTED_INGESTION_EXTENSIONS = frozenset({".pdf"})


def _default_max_file_size_bytes() -> int:
    try:
        from src.config.settings import ingestion_settings

        return ingestion_settings.max_file_size_mb * 1024 * 1024
    except Exception:
        return 2**63 - 1


class IngestionRequestValidator(Validator["IngestionRequest"]):
    def validate(self, value: "IngestionRequest") -> ValidationResult:
        from src.application.workflows.ingestion.ingestion_request import (
            IngestionRequest,
        )

        if not isinstance(value, IngestionRequest):
            raise TypeError("IngestionRequestValidator expects an IngestionRequest.")

        result = ValidationResult()

        file_path = (value.file_path or "").strip()
        if not file_path:
            result.add_issue(
                "file_path",
                "File path is required.",
                "ingestion.file_path.required",
            )
            return result

        resolved_path = Path(file_path)
        if not resolved_path.exists():
            result.add_issue(
                "file_path",
                "Input file does not exist.",
                "ingestion.file_path.not_found",
            )
            return result

        if not resolved_path.is_file():
            result.add_issue(
                "file_path",
                "Input path must be a file.",
                "ingestion.file_path.not_file",
            )
            return result

        extension = resolved_path.suffix.lower()
        if extension not in _SUPPORTED_INGESTION_EXTENSIONS:
            result.add_issue(
                "file_path",
                "Unsupported file extension for ingestion.",
                "ingestion.file_path.unsupported_extension",
            )

        try:
            file_size_bytes = resolved_path.stat().st_size
        except OSError:
            result.add_issue(
                "file_path",
                "Input file is not readable.",
                "ingestion.file_path.unreadable",
            )
            file_size_bytes = None

        max_file_size_bytes = _default_max_file_size_bytes()
        if (
            file_size_bytes is not None
            and file_size_bytes > max_file_size_bytes
        ):
            result.add_issue(
                "file_path",
                "Input file exceeds the configured maximum file size.",
                "ingestion.file_path.file_too_large",
            )

        if value.document_type is not None:
            normalized_document_type = value.document_type.strip().lower()
            if normalized_document_type not in {
                document_type.value
                for document_type in DocumentType
            }:
                result.add_issue(
                    "document_type",
                    "Unsupported document type.",
                    "ingestion.document_type.invalid",
                )

        for field_name in ("force", "run_quality_checks", "trace"):
            raw_value = getattr(value, field_name)
            if not isinstance(raw_value, bool):
                result.add_issue(
                    field_name,
                    f"{field_name} must be a boolean.",
                    f"ingestion.{field_name}.invalid",
                )

        for field_name in ("generate_questions", "enable_ocr"):
            raw_value = getattr(value, field_name)
            if raw_value is not None and not isinstance(raw_value, bool):
                result.add_issue(
                    field_name,
                    f"{field_name} must be a boolean when provided.",
                    f"ingestion.{field_name}.invalid",
                )

        return result
