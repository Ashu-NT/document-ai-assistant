from __future__ import annotations

"""
Ingest a single document into the corpus without using the benchmark truth set.

Usage:
    python scripts/ingest_document.py --input data/input/example.pdf
    python scripts/ingest_document.py --input-dir data/input
    python scripts/ingest_document.py --input data/input/example.pdf --document-type manual
    python scripts/ingest_document.py --reingest-document-id doc_123
"""

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"

for _import_root in (PROJECT_ROOT, SRC_ROOT, SCRIPTS_ROOT):
    _import_root_text = str(_import_root)
    if _import_root_text not in sys.path:
        sys.path.insert(0, _import_root_text)

from ingest_document_batch_support import (
    build_batch_json_payload,
    run_recursive_pdf_batch,
    run_reingestion_request,
    run_single_input_path,
    validate_ingest_document_args,
)
from src.shared.exceptions import ApplicationError
from src.shared.formatting.ingestion_result_formatter import (
    build_ingestion_json_payload,
    print_ingestion_result,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest one document or recursively ingest all PDFs in a folder."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        help="Path to the PDF/document to ingest.",
    )
    input_group.add_argument(
        "--input-dir",
        help="Path to a folder whose PDFs should be ingested recursively.",
    )
    input_group.add_argument(
        "--reingest-document-id",
        help="Reparse and replace one existing document in place by document_id.",
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
    parser.add_argument(
        "--reingest-if-duplicate",
        action="store_true",
        help=(
            "When ingesting by --input, automatically reingest the existing "
            "document in place if a duplicate is detected."
        ),
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    validate_ingest_document_args(parser, args)
    return args


def print_status(message: str) -> None:
    print(f"[ingest-document] {message}", flush=True)


def _build_runtime():
    from src.application.orchestrator.ingestion import (  # noqa: WPS433
        build_ingestion_runtime,
    )

    return build_ingestion_runtime()


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = None

    try:
        input_path = None
        input_dir = None
        if args.input is not None:
            input_path = Path(args.input).expanduser().resolve()
            if not input_path.exists():
                print(f"Input file not found: {input_path}", file=sys.stderr)
                return 1
        if args.input_dir is not None:
            input_dir = Path(args.input_dir).expanduser().resolve()
            if not input_dir.exists() or not input_dir.is_dir():
                print(f"Input directory not found: {input_dir}", file=sys.stderr)
                return 1

        if not args.json:
            if input_path is not None:
                print_status(f"Input path: {input_path}")
            elif input_dir is not None:
                print_status(f"Input directory: {input_dir}")
            else:
                print_status(
                    f"Reingest target document ID: {args.reingest_document_id}"
                )
            print_status("Building ingestion runtime...")
        runtime = _build_runtime()
        if not args.json:
            print_status("Ingestion runtime ready.")
            if input_path is not None:
                print_status(f"Starting ingestion for {input_path.name}...")
            elif input_dir is not None:
                print_status("Starting recursive PDF ingestion...")
            else:
                print_status(
                    f"Starting in-place reingestion for {args.reingest_document_id}..."
                )

        progress_callback = None if args.json else print_status
        if args.reingest_document_id is not None:
            result = run_reingestion_request(
                args,
                runtime,
                progress_callback=progress_callback,
            )
        elif input_dir is not None:
            batch_summary = run_recursive_pdf_batch(
                input_dir,
                run_for_path=lambda path, index, total: run_single_input_path(
                    args,
                    runtime,
                    input_path=path,
                    progress_callback=progress_callback,
                    batch_index=index,
                    batch_total=total,
                ),
                status_callback=progress_callback,
            )
            if batch_summary.discovered_count == 0:
                message = f"No PDF files found under: {input_dir}"
                if args.json:
                    print(
                        json.dumps(
                            {
                                "mode": "batch",
                                "input_dir": str(input_dir),
                                "discovered_count": 0,
                                "succeeded_count": 0,
                                "failed_count": 0,
                                "results": [],
                                "failures": [],
                                "error": message,
                            },
                            indent=2,
                        )
                    )
                else:
                    print(message, file=sys.stderr)
                return 1
            if args.json:
                print(
                    json.dumps(
                        build_batch_json_payload(
                            batch_summary,
                            result_payload_builder=build_ingestion_json_payload,
                        ),
                        indent=2,
                    )
                )
            else:
                print_status(
                    "Recursive ingestion completed "
                    f"({batch_summary.succeeded_count}/{batch_summary.discovered_count} "
                    "PDFs succeeded)."
                )
                for result in batch_summary.results:
                    print()
                    print_ingestion_result(result)
                if batch_summary.failures:
                    print("\nFailures")
                    print("--------")
                    for failure in batch_summary.failures:
                        print(f"- {failure.input_path}: {failure.error}")
            return 0 if batch_summary.failed_count == 0 else 1
        else:
            result = run_single_input_path(
                args,
                runtime,
                input_path=input_path,
                progress_callback=progress_callback,
            )

        if args.json:
            print(json.dumps(build_ingestion_json_payload(result), indent=2))
        else:
            print_status("Ingestion completed.")
            print()
            print_ingestion_result(result)

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
