from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(slots=True)
class BatchIngestionFailure:
    input_path: str
    error: str


@dataclass(slots=True)
class BatchIngestionSummary:
    input_dir: str
    discovered_count: int
    results: list[Any]
    failures: list[BatchIngestionFailure]

    @property
    def succeeded_count(self) -> int:
        return len(self.results)

    @property
    def failed_count(self) -> int:
        return len(self.failures)


def discover_recursive_pdf_inputs(input_dir: Path) -> list[Path]:
    return sorted(
        path.resolve()
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )


def run_recursive_pdf_batch(
    input_dir: Path,
    *,
    run_for_path: Callable[[Path, int, int], Any],
    status_callback: Callable[[str], None] | None = None,
) -> BatchIngestionSummary:
    input_paths = discover_recursive_pdf_inputs(input_dir)
    results: list[Any] = []
    failures: list[BatchIngestionFailure] = []
    total = len(input_paths)

    for index, input_path in enumerate(input_paths, start=1):
        if status_callback is not None:
            status_callback(
                f"[{index}/{total}] Preparing ingestion for {input_path.name}..."
            )
        try:
            results.append(run_for_path(input_path, index, total))
        except Exception as exc:
            message = str(exc) or exc.__class__.__name__
            failures.append(
                BatchIngestionFailure(
                    input_path=str(input_path),
                    error=message,
                )
            )
            if status_callback is not None:
                status_callback(f"[{index}/{total}] FAILED {input_path.name}: {message}")

    return BatchIngestionSummary(
        input_dir=str(input_dir),
        discovered_count=total,
        results=results,
        failures=failures,
    )


def build_batch_json_payload(
    summary: BatchIngestionSummary,
    *,
    result_payload_builder: Callable[[Any], dict[str, Any]],
) -> dict[str, Any]:
    return {
        "mode": "batch",
        "input_dir": summary.input_dir,
        "discovered_count": summary.discovered_count,
        "succeeded_count": summary.succeeded_count,
        "failed_count": summary.failed_count,
        "results": [result_payload_builder(result) for result in summary.results],
        "failures": [
            {
                "input_path": failure.input_path,
                "error": failure.error,
            }
            for failure in summary.failures
        ],
    }


def validate_ingest_document_args(parser, args) -> None:
    if args.reingest_document_id and args.reingest_if_duplicate:
        parser.error(
            "--reingest-if-duplicate only applies to --input mode, not "
            "--reingest-document-id."
        )
    if args.input_dir is not None and args.title:
        parser.error(
            "--title is only supported for single-document --input mode, not "
            "recursive --input-dir mode."
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


def run_reingestion_request(
    args,
    runtime,
    *,
    progress_callback,
    document_id: str | None = None,
):
    from src.application.workflows.ingestion import ReingestionRequest  # noqa: WPS433

    return runtime.ingestion_workflow.reingest(
        ReingestionRequest(
            document_id=document_id or args.reingest_document_id,
            run_quality_checks=not args.skip_quality_checks,
            requested_by="ingest_document_script_reingest",
        ),
        progress_callback=progress_callback,
    )


def run_ingestion_request(
    args,
    runtime,
    *,
    progress_callback,
    input_path: Path | None = None,
):
    from src.application.workflows.ingestion import IngestionRequest  # noqa: WPS433

    return runtime.ingestion_workflow.run(
        IngestionRequest(
            file_path=str((input_path or Path(args.input)).expanduser().resolve()),
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


def run_single_input_path(
    args,
    runtime,
    *,
    input_path: Path,
    progress_callback,
    batch_index: int = 1,
    batch_total: int = 1,
):
    prefixed_progress = _build_progress_callback(
        progress_callback=progress_callback,
        batch_index=batch_index,
        batch_total=batch_total,
    )
    result = run_ingestion_request(
        args,
        runtime,
        progress_callback=prefixed_progress,
        input_path=input_path,
    )
    if args.reingest_if_duplicate and _is_duplicate_result(result):
        existing_document_id = result.duplicate_of_document_id or result.document_id
        if existing_document_id:
            if prefixed_progress is not None:
                prefixed_progress(
                    "Duplicate detected. Upgrading to safe in-place reingestion "
                    f"for {existing_document_id}..."
                )
            result = run_reingestion_request(
                args,
                runtime,
                progress_callback=prefixed_progress,
                document_id=existing_document_id,
            )
    return result


def _is_duplicate_result(result) -> bool:
    status_value = getattr(result.status, "value", "")
    return status_value in {
        "skipped_file_duplicate",
        "skipped_content_duplicate",
    }


def _build_progress_callback(*, progress_callback, batch_index: int, batch_total: int):
    if progress_callback is None:
        return None
    if batch_total <= 1:
        return progress_callback

    def _prefixed(message: str) -> None:
        progress_callback(f"[{batch_index}/{batch_total}] {message}")

    return _prefixed
