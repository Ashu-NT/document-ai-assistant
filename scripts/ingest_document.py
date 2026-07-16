from __future__ import annotations

"""
Ingest a single document into the corpus without using the benchmark truth set.

Usage:
    python scripts/ingest_document.py --input data/input/example.pdf
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

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_text = str(_import_root)
    if _import_root_text not in sys.path:
        sys.path.insert(0, _import_root_text)

from src.shared.exceptions import ApplicationError
from src.shared.formatting.ingestion_result_formatter import (
    build_ingestion_json_payload,
    print_ingestion_result,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest one document through the canonical ingestion workflow."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        help="Path to the PDF/document to ingest.",
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
    _validate_args(parser, args)
    return args


def print_status(message: str) -> None:
    print(f"[ingest-document] {message}", flush=True)


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.reingest_document_id and args.reingest_if_duplicate:
        parser.error(
            "--reingest-if-duplicate only applies to --input mode, not "
            "--reingest-document-id."
        )

    if args.reingest_document_id is None:
        if args.force and args.reingest_if_duplicate:
            parser.error(
                "--force bypasses duplicate detection, so it cannot be combined "
                "with --reingest-if-duplicate."
            )
        return

    conflicting_flags: list[str] = []
    for flag_name in (
        "document_type",
        "title",
        "source_name",
        "force",
        "generate_questions",
        "enable_ocr",
        "trace",
    ):
        value = getattr(args, flag_name)
        if value not in (None, False):
            conflicting_flags.append(f"--{flag_name.replace('_', '-')}")

    if conflicting_flags:
        parser.error(
            "--reingest-document-id uses the stored file path and stored document "
            "metadata, so these flags are not supported with it: "
            + ", ".join(conflicting_flags)
        )


def _build_runtime():
    from src.application.orchestrator.ingestion import (  # noqa: WPS433
        build_ingestion_runtime,
    )

    return build_ingestion_runtime()


def _run_reingestion(args, runtime, *, progress_callback):
    from src.application.workflows.ingestion import ReingestionRequest  # noqa: WPS433

    return runtime.ingestion_workflow.reingest(
        ReingestionRequest(
            document_id=args.reingest_document_id,
            run_quality_checks=not args.skip_quality_checks,
            requested_by="ingest_document_script_reingest",
        ),
        progress_callback=progress_callback,
    )


def _run_ingestion(args, runtime, *, progress_callback):
    from src.application.workflows.ingestion import IngestionRequest  # noqa: WPS433

    return runtime.ingestion_workflow.run(
        IngestionRequest(
            file_path=str(Path(args.input).expanduser().resolve()),
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
        progress_callback=progress_callback,
    )


def _is_duplicate_result(result) -> bool:
    status_value = getattr(result.status, "value", "")
    return status_value in {
        "skipped_file_duplicate",
        "skipped_content_duplicate",
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = None

    try:
        input_path = None
        if args.input is not None:
            input_path = Path(args.input).expanduser().resolve()
            if not input_path.exists():
                print(f"Input file not found: {input_path}", file=sys.stderr)
                return 1

        if not args.json:
            if input_path is not None:
                print_status(f"Input path: {input_path}")
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
            else:
                print_status(
                    f"Starting in-place reingestion for {args.reingest_document_id}..."
                )

        progress_callback = None if args.json else print_status
        if args.reingest_document_id is not None:
            result = _run_reingestion(
                args,
                runtime,
                progress_callback=progress_callback,
            )
        else:
            result = _run_ingestion(
                args,
                runtime,
                progress_callback=progress_callback,
            )
            if args.reingest_if_duplicate and _is_duplicate_result(result):
                existing_document_id = result.duplicate_of_document_id or result.document_id
                if existing_document_id:
                    if not args.json:
                        print_status(
                            "Duplicate detected. Upgrading to safe in-place "
                            f"reingestion for {existing_document_id}..."
                        )
                    args.reingest_document_id = existing_document_id
                    result = _run_reingestion(
                        args,
                        runtime,
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
