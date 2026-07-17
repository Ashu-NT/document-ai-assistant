from __future__ import annotations

from typing import Any


def build_ingestion_json_payload(result) -> dict[str, Any]:
    diagnostics = result.diagnostics
    return {
        "status": result.status.value,
        "ingestion_run_id": result.ingestion_run_id,
        "document_id": result.document_id,
        "title": result.title,
        "file_name": result.file_name,
        "document_type": result.document_type,
        "page_count": result.page_count,
        "section_count": result.section_count,
        "element_count": result.element_count,
        "chunk_count": result.chunk_count,
        "table_count": result.table_count,
        "picture_count": result.picture_count,
        "identifier_count": result.identifier_count,
        "generated_question_count": result.generated_question_count,
        "vector_count": result.vector_count,
        "runtime_profile": diagnostics.get("ingestion_runtime_profile"),
        "requested_runtime_profile": diagnostics.get("requested_runtime_profile"),
        "duplicate_of_document_id": result.duplicate_of_document_id,
        "warnings": result.warnings,
        "errors": result.errors,
        "diagnostics": diagnostics,
        "current_stage": (
            result.current_stage.value if result.current_stage is not None else None
        ),
        "correlation_id": result.correlation_id,
    }


def print_ingestion_result(result) -> None:
    print(f"Status           : {result.status.value}")
    print(f"Document ID      : {result.document_id or '-'}")
    print(f"Title            : {result.title or '-'}")
    print(f"File Name        : {result.file_name or '-'}")
    print(f"Document Type    : {result.document_type or '-'}")
    print(f"Pages            : {_display(result.page_count)}")
    print(f"Sections         : {_display(result.section_count)}")
    print(f"Elements         : {_display(result.element_count)}")
    print(f"Chunks           : {_display(result.chunk_count)}")
    print(f"Tables           : {_display(result.table_count)}")
    print(f"Pictures         : {_display(result.picture_count)}")
    print(f"Identifiers      : {_display(result.identifier_count)}")
    print(f"Generated Qs     : {_display(result.generated_question_count)}")
    print(f"Vectors          : {_display(result.vector_count)}")
    runtime_profile = result.diagnostics.get("ingestion_runtime_profile")
    extraction_skipped = bool(result.diagnostics.get("extraction_skipped"))
    print(f"Runtime Profile  : {_display(runtime_profile)}")
    print(f"Extraction       : {'skipped by config' if extraction_skipped else 'enabled'}")

    if result.duplicate_of_document_id:
        print(f"Duplicate Of     : {result.duplicate_of_document_id}")

    if not result.warnings:
        return

    print("\nWarnings")
    print("--------")
    for warning in result.warnings:
        print(f"- {warning}")


def _display(value: object) -> object:
    return value if value is not None else "-"
