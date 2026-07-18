from __future__ import annotations

"""
Diagnostic-only report over already-persisted `chunk_cross_references` rows
(populated by `ChunkCrossReferenceLinker`, either during ingestion when
`CHUNK_CROSS_REFERENCE_DETECTION_ENABLED` is set, or via
`scripts/backfill_chunk_cross_references.py`).

This does not re-run detection/resolution -- it reads what was actually
persisted and summarizes it, so a human can decide whether the
resolved-unique/resolved-ambiguous/unresolved mix looks right before turning
on `RETRIEVAL_CROSS_REFERENCE_EXPANSION_ENABLED` (or the detection flag
itself, for future ingestion runs).

What to look for:
  - A high `unresolved` rate for `page_reference` rows suggests either the
    target pages genuinely aren't chunked (drawings/appendices) or the
    detector's page numbers are off -- read the `--show-samples` output and
    check the matched_text against the source chunk's content.
  - `resolved_ambiguous` isn't inherently wrong (the tie-break logic picks a
    real, sensible candidate -- see `ChunkCrossReferenceResolver`), but a
    document where nearly everything is ambiguous usually means that
    document is very densely chunked (many chunks share a page), not that
    resolution quality is poor; spot-check a few before trusting the rate.
  - `section_reference` rows are ALWAYS unresolved in v1 by design (see
    `ChunkCrossReferenceType.SECTION_REFERENCE`) -- this is not a defect,
    just a recorded-for-visibility signal for the deferred phase-2 work.

Usage:
    # Full corpus summary
    python scripts/report_chunk_cross_reference_candidates.py

    # One document only
    python scripts/report_chunk_cross_reference_candidates.py --document-id doc_001

    # Show more/fewer sample rows per bucket
    python scripts/report_chunk_cross_reference_candidates.py --show-samples 10

    # Machine-readable output
    python scripts/report_chunk_cross_reference_candidates.py --json
"""

import argparse
import json
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

DEFAULT_SAMPLE_ROWS = 5


@dataclass(slots=True)
class CrossReferenceRow:
    cross_reference_id: str
    source_chunk_id: str
    target_chunk_id: str | None
    reference_type: str
    matched_text: str
    target_page: int | None
    target_section_label: str | None
    resolution_status: str
    confidence_score: float
    source_content_preview: str
    target_content_preview: str | None


@dataclass(slots=True)
class DocumentReport:
    document_id: str
    file_name: str | None
    rows: list[CrossReferenceRow] = field(default_factory=list)

    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self.rows:
            key = f"{row.reference_type}:{row.resolution_status}"
            counts[key] = counts.get(key, 0) + 1
        return counts


def _preview(text: str | None, *, length: int = 160) -> str:
    if not text:
        return ""
    flattened = " ".join(text.split())
    return flattened[:length]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--document-id",
        default=None,
        help="Only report cross references belonging to this document ID.",
    )
    parser.add_argument(
        "--show-samples",
        type=int,
        default=DEFAULT_SAMPLE_ROWS,
        help=f"Sample rows to print per status bucket (default: {DEFAULT_SAMPLE_ROWS}).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of a human-readable report.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[chunk-cross-reference-report] {message}", flush=True)


def print_report(reports: list[DocumentReport], *, show_samples: int) -> None:
    if not reports:
        print("No chunk cross references found. Has the backfill script been run?")
        return

    total_rows = sum(len(report.rows) for report in reports)
    overall_counts: dict[str, int] = {}
    for report in reports:
        for key, count in report.status_counts().items():
            overall_counts[key] = overall_counts.get(key, 0) + count

    print(
        f"{total_rows} chunk cross reference(s) across {len(reports)} document(s).\n"
    )
    print("Overall breakdown (reference_type:resolution_status -> count):")
    for key, count in sorted(overall_counts.items(), key=lambda item: -item[1]):
        print(f"  {key}: {count}")
    print()

    for report in sorted(reports, key=lambda r: len(r.rows), reverse=True):
        print(f"=== {report.document_id}  ({report.file_name or '?'}) ===")
        print(f"  total: {len(report.rows)}  {report.status_counts()}")

        by_status: dict[str, list[CrossReferenceRow]] = {}
        for row in report.rows:
            by_status.setdefault(row.resolution_status, []).append(row)

        for status_name, rows in by_status.items():
            print(f"  --- {status_name} samples ---")
            for row in rows[:show_samples]:
                target_desc = (
                    f"-> {row.target_chunk_id} ({_preview(row.target_content_preview, length=100)})"
                    if row.target_chunk_id
                    else "-> (unresolved)"
                )
                print(
                    f"    [{row.reference_type}] {row.matched_text!r} "
                    f"page={row.target_page} section={row.target_section_label} "
                    f"conf={row.confidence_score} {target_desc}"
                )
                print(f"        source: {_preview(row.source_content_preview)}")
        print()


def to_json(reports: list[DocumentReport]) -> list[dict[str, Any]]:
    return [
        {
            "document_id": report.document_id,
            "file_name": report.file_name,
            "status_counts": report.status_counts(),
            "rows": [
                {
                    "cross_reference_id": row.cross_reference_id,
                    "source_chunk_id": row.source_chunk_id,
                    "target_chunk_id": row.target_chunk_id,
                    "reference_type": row.reference_type,
                    "matched_text": row.matched_text,
                    "target_page": row.target_page,
                    "target_section_label": row.target_section_label,
                    "resolution_status": row.resolution_status,
                    "confidence_score": row.confidence_score,
                }
                for row in report.rows
            ],
        }
        for report in reports
    ]


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None

    try:
        from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
        from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
            __all__ as _orm_models_loaded,
        )
        from src.infrastructure.db.orm_models.document_models import (  # noqa: WPS433
            ChunkCrossReferenceORM,
            ChunkORM,
            DocumentORM,
        )
        from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
        from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433

        bootstrap_application()
        ensure_database_schema(engine)
        session = SessionLocal()

        print_status("Loading chunk cross references...")
        source_chunk = ChunkORM
        target_chunk = ChunkORM.__table__.alias("target_chunk")

        query = session.query(
            ChunkCrossReferenceORM.id,
            ChunkCrossReferenceORM.document_id,
            ChunkCrossReferenceORM.source_chunk_id,
            ChunkCrossReferenceORM.target_chunk_id,
            ChunkCrossReferenceORM.reference_type,
            ChunkCrossReferenceORM.matched_text,
            ChunkCrossReferenceORM.target_page,
            ChunkCrossReferenceORM.target_section_label,
            ChunkCrossReferenceORM.resolution_status,
            ChunkCrossReferenceORM.confidence_score,
            source_chunk.content,
            target_chunk.c.content,
        ).outerjoin(
            source_chunk, source_chunk.id == ChunkCrossReferenceORM.source_chunk_id
        ).outerjoin(
            target_chunk, target_chunk.c.id == ChunkCrossReferenceORM.target_chunk_id
        )
        if args.document_id:
            query = query.filter(
                ChunkCrossReferenceORM.document_id == args.document_id
            )
        rows = query.all()

        if not rows:
            print("No chunk cross references found for the given filter.")
            return 0

        print_status(f"Summarizing {len(rows)} cross reference(s)...")

        reports_by_document: dict[str, DocumentReport] = {}
        document_ids = {row[1] for row in rows}
        file_names_by_document_id: dict[str, str] = {}
        for document_id, file_name in session.query(
            DocumentORM.id, DocumentORM.file_name
        ).filter(DocumentORM.id.in_(document_ids)):
            file_names_by_document_id[document_id] = file_name

        for (
            cross_reference_id,
            document_id,
            source_chunk_id,
            target_chunk_id,
            reference_type,
            matched_text,
            target_page,
            target_section_label,
            resolution_status,
            confidence_score,
            source_content,
            target_content,
        ) in rows:
            report = reports_by_document.get(document_id)
            if report is None:
                report = DocumentReport(
                    document_id=document_id,
                    file_name=file_names_by_document_id.get(document_id),
                )
                reports_by_document[document_id] = report

            report.rows.append(
                CrossReferenceRow(
                    cross_reference_id=cross_reference_id,
                    source_chunk_id=source_chunk_id,
                    target_chunk_id=target_chunk_id,
                    reference_type=reference_type,
                    matched_text=matched_text,
                    target_page=target_page,
                    target_section_label=target_section_label,
                    resolution_status=resolution_status,
                    confidence_score=confidence_score,
                    source_content_preview=_preview(source_content),
                    target_content_preview=_preview(target_content) if target_content else None,
                )
            )

        reports = list(reports_by_document.values())

        if args.json:
            print(json.dumps(to_json(reports), indent=2))
        else:
            print_report(reports, show_samples=args.show_samples)

        return 0

    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    raise SystemExit(main())
