from __future__ import annotations

"""
Ingest a single document into the corpus without using the benchmark truth set.

Usage:
    python scripts/ingest_document.py --input data/input/example.pdf
    python scripts/ingest_document.py --input data/input/example.pdf --document-type manual
"""

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_text = str(_import_root)
    if _import_root_text not in sys.path:
        sys.path.insert(0, _import_root_text)

from src.shared.exceptions import ApplicationError


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest one document through the canonical ingestion workflow."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the PDF/document to ingest.",
    )
    parser.add_argument(
        "--document-type",
        help="Optional document type hint, for example manual or datasheet.",
    )
    parser.add_argument(
        "--title",
        help="Optional display title to store for the document.",
    )
    parser.add_argument(
        "--source-name",
        help="Optional source name to store on the document.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass duplicate checks for this ingest request.",
    )
    parser.add_argument(
        "--generate-questions",
        action="store_true",
        help="Request question generation for final chunks.",
    )
    ocr_group = parser.add_mutually_exclusive_group()
    ocr_group.add_argument(
        "--enable-ocr",
        dest="enable_ocr",
        action="store_true",
        help="Force OCR on for this ingest request.",
    )
    ocr_group.add_argument(
        "--disable-ocr",
        dest="enable_ocr",
        action="store_false",
        help="Force OCR off for this ingest request.",
    )
    parser.set_defaults(enable_ocr=None)
    parser.add_argument(
        "--skip-quality-checks",
        action="store_true",
        help="Skip ingestion quality checks.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Enable ingestion trace diagnostics.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the ingestion result as JSON.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[ingest-document] {message}", flush=True)


def build_json_payload(result) -> dict[str, Any]:
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
        "duplicate_of_document_id": result.duplicate_of_document_id,
        "warnings": result.warnings,
        "errors": result.errors,
        "diagnostics": result.diagnostics,
        "current_stage": (
            result.current_stage.value if result.current_stage is not None else None
        ),
        "correlation_id": result.correlation_id,
    }


def print_result(result) -> None:
    print(f"Status           : {result.status.value}")
    print(f"Document ID      : {result.document_id or '-'}")
    print(f"Title            : {result.title or '-'}")
    print(f"File Name        : {result.file_name or '-'}")
    print(f"Document Type    : {result.document_type or '-'}")
    print(f"Pages            : {result.page_count if result.page_count is not None else '-'}")
    print(
        f"Sections         : {result.section_count if result.section_count is not None else '-'}"
    )
    print(
        f"Elements         : {result.element_count if result.element_count is not None else '-'}"
    )
    print(f"Chunks           : {result.chunk_count if result.chunk_count is not None else '-'}")
    print(f"Tables           : {result.table_count if result.table_count is not None else '-'}")
    print(
        f"Pictures         : {result.picture_count if result.picture_count is not None else '-'}"
    )
    print(
        "Identifiers      : "
        f"{result.identifier_count if result.identifier_count is not None else '-'}"
    )
    print(
        "Generated Qs     : "
        f"{result.generated_question_count if result.generated_question_count is not None else '-'}"
    )
    print(f"Vectors          : {result.vector_count if result.vector_count is not None else '-'}")
    extraction_skipped = bool(result.diagnostics.get("extraction_skipped"))
    print(f"Extraction       : {'skipped by config' if extraction_skipped else 'enabled'}")

    if result.duplicate_of_document_id:
        print(f"Duplicate Of     : {result.duplicate_of_document_id}")

    if result.warnings:
        print("\nWarnings")
        print("--------")
        for warning in result.warnings:
            print(f"- {warning}")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = None

    try:
        input_path = Path(args.input).expanduser().resolve()
        if not input_path.exists():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            return 1

        from src.application.orchestrator.ingestion import (  # noqa: WPS433
            build_ingestion_runtime,
        )
        from src.application.workflows.ingestion import IngestionRequest  # noqa: WPS433

        if not args.json:
            print_status(f"Input path: {input_path}")
            print_status("Building ingestion runtime...")
        runtime = build_ingestion_runtime()
        if not args.json:
            print_status("Ingestion runtime ready.")
            print_status(f"Starting ingestion for {input_path.name}...")

        result = runtime.ingestion_workflow.run(
            IngestionRequest(
                file_path=str(input_path),
                document_type=args.document_type,
                title=args.title,
                source_name=args.source_name,
                force=args.force,
                generate_questions=args.generate_questions,
                enable_ocr=args.enable_ocr,
                run_quality_checks=not args.skip_quality_checks,
                trace=args.trace,
                requested_by="ingest_document_script",
            ),
            progress_callback=None if args.json else print_status,
        )

        if args.json:
            print(json.dumps(build_json_payload(result), indent=2))
        else:
            print_status("Ingestion completed.")
            print()
            print_result(result)

        return 0

    except ApplicationError as exc:  # type: ignore[misc]
        print(str(exc), file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if runtime is not None:
            runtime.close()


if __name__ == "__main__":
    raise SystemExit(main())
