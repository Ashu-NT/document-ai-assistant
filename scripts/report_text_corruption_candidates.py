from __future__ import annotations

"""
Diagnostic-only scan for "missing-letter/missing-space" text corruption
across the ingested corpus.

Background: some PDFs embed a subset font with a broken/incomplete
ToUnicode CMap. When the Unicode replacement character (U+FFFD) shows up
instead, that is already detected and handled by `PageTextQualityAnalyzer`/
`OCRTargetSelector` (see `has_corrupted_text`). This script targets the
OTHER variant of the same underlying defect: some glyph IDs -- including
the space glyph and certain narrow letters -- decode to an EMPTY STRING
instead of a replacement character, so characters are silently dropped
rather than replaced with a detectable marker. The result reads like
"Wecertifythattheteslresulfromlestson..." instead of "We certify that the
test result from tests on...".

Detection approach and its limits (read before trusting the output):

  A chunk is flagged when it contains several (>= --min-run-count, default
  3) contiguous runs of plain alphabetic characters (letters only -- no
  digits, hyphens, or spaces) at least --min-run-length (default 20)
  characters long. Digits/hyphens are deliberately excluded from what
  counts as a "run" so this does not overlap with legitimate dense
  identifiers ("6ES7131-6BF00-0CA0"), which was the reason a naive
  word-length heuristic was rejected in an earlier pass.

  This heuristic has a CONFIRMED, non-trivial false-positive rate: a
  single long word in a language with heavy compounding (German technical
  vocabulary especially -- "Isolationswiderstand", "Kabelbefestigungspunkt")
  is completely legitimate and can exceed the length threshold on its own.
  Requiring several such runs in the same chunk (not just one) substantially
  reduces this, since genuine corruption merges MULTIPLE separate words
  together repeatedly in the same passage, but it does not eliminate it.

  Because of this, this script is intentionally NOT wired into the
  ingestion pipeline or the OCR-fallback selection logic -- it only reports
  candidates for a human to look at. Every document/chunk this script
  flags needs manual confirmation (read the sample runs printed below --
  genuine corruption reads as several real, complete words mashed
  together, e.g. "affiliatesandsubsidiaries"; a false positive reads as one
  single, correctly-spelled, unusually long word).

Usage:
    # Scan the full corpus
    python scripts/report_text_corruption_candidates.py

    # Scan one document only
    python scripts/report_text_corruption_candidates.py --document-id doc_123

    # Tune sensitivity
    python scripts/report_text_corruption_candidates.py --min-run-length 25 --min-run-count 2

    # Machine-readable output
    python scripts/report_text_corruption_candidates.py --json
"""

import argparse
import json
import re
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from sqlalchemy import Row

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

DEFAULT_MIN_RUN_LENGTH = 20
DEFAULT_MIN_RUN_COUNT = 3
DEFAULT_SAMPLE_RUNS = 5

# Unicode letters only (any script/language) -- excludes digits, underscore,
# hyphen, and whitespace, so this never fires on dense alphanumeric
# identifiers or hyphenated part numbers.
_ALPHA_RUN_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)


def find_long_alpha_runs(text: str, *, min_run_length: int) -> list[str]:
    if not text:
        return []
    return [
        run for run in _ALPHA_RUN_PATTERN.findall(text) if len(run) >= min_run_length
    ]


def is_corruption_candidate(
    text: str,
    *,
    min_run_length: int,
    min_run_count: int,
) -> bool:
    runs = find_long_alpha_runs(text, min_run_length=min_run_length)
    return len(runs) >= min_run_count


@dataclass(slots=True)
class ChunkCandidate:
    chunk_id: str
    document_id: str
    page_start: int | None
    page_end: int | None
    run_count: int
    sample_runs: list[str]


@dataclass(slots=True)
class DocumentCandidateGroup:
    document_id: str
    file_name: str | None
    chunk_candidates: list[ChunkCandidate] = field(default_factory=list)


def scan_chunk_rows(
    rows: Sequence[Row[tuple[str, str, str, int | None, int | None]]],
    *,
    min_run_length: int,
    min_run_count: int,
) -> list[ChunkCandidate]:
    """rows: (chunk_id, document_id, content, page_start, page_end)."""
    candidates: list[ChunkCandidate] = []
    for chunk_id, document_id, content, page_start, page_end in rows:
        runs = find_long_alpha_runs(content, min_run_length=min_run_length)
        if len(runs) < min_run_count:
            continue
        candidates.append(
            ChunkCandidate(
                chunk_id=chunk_id,
                document_id=document_id,
                page_start=page_start,
                page_end=page_end,
                run_count=len(runs),
                sample_runs=runs[:DEFAULT_SAMPLE_RUNS],
            )
        )
    return candidates


def group_by_document(
    candidates: list[ChunkCandidate],
    file_names_by_document_id: dict[str, str],
) -> list[DocumentCandidateGroup]:
    groups: dict[str, DocumentCandidateGroup] = {}
    for candidate in candidates:
        group = groups.get(candidate.document_id)
        if group is None:
            group = DocumentCandidateGroup(
                document_id=candidate.document_id,
                file_name=file_names_by_document_id.get(candidate.document_id),
            )
            groups[candidate.document_id] = group
        group.chunk_candidates.append(candidate)

    return sorted(
        groups.values(),
        key=lambda group: len(group.chunk_candidates),
        reverse=True,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--document-id",
        default=None,
        help="Only scan chunks belonging to this document ID.",
    )
    parser.add_argument(
        "--min-run-length",
        type=int,
        default=DEFAULT_MIN_RUN_LENGTH,
        help=f"Minimum length of a contiguous alphabetic run to count (default: {DEFAULT_MIN_RUN_LENGTH}).",
    )
    parser.add_argument(
        "--min-run-count",
        type=int,
        default=DEFAULT_MIN_RUN_COUNT,
        help=(
            "Minimum number of qualifying runs a chunk must contain to be "
            f"flagged (default: {DEFAULT_MIN_RUN_COUNT})."
        ),
    )
    parser.add_argument(
        "--show-samples",
        type=int,
        default=DEFAULT_SAMPLE_RUNS,
        help=f"Sample runs to print per flagged chunk (default: {DEFAULT_SAMPLE_RUNS}).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of a human-readable report.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[text-corruption-scan] {message}", flush=True)


def print_report(groups: list[DocumentCandidateGroup], *, show_samples: int) -> None:
    if not groups:
        print("No candidates found with the current thresholds.")
        return

    total_chunks = sum(len(group.chunk_candidates) for group in groups)
    print(
        f"Flagged {total_chunks} chunk(s) across {len(groups)} document(s). "
        "This is a HEURISTIC -- confirm each one manually before acting on it "
        "(see the script's module docstring for known false-positive shapes).\n"
    )

    for group in groups:
        print(f"=== {group.document_id}  ({group.file_name or '?'}) ===")
        print(f"  flagged chunks: {len(group.chunk_candidates)}")
        for candidate in group.chunk_candidates[:3]:
            pages = (
                f"p{candidate.page_start}"
                if candidate.page_start == candidate.page_end
                else f"p{candidate.page_start}-{candidate.page_end}"
            )
            print(
                f"    - {candidate.chunk_id} ({pages}, "
                f"{candidate.run_count} long run(s)):"
            )
            for sample in candidate.sample_runs[:show_samples]:
                print(f"        {sample!r}")
        print()


def to_json(groups: list[DocumentCandidateGroup]) -> list[dict[str, Any]]:
    return [
        {
            "document_id": group.document_id,
            "file_name": group.file_name,
            "flagged_chunk_count": len(group.chunk_candidates),
            "chunks": [
                {
                    "chunk_id": candidate.chunk_id,
                    "page_start": candidate.page_start,
                    "page_end": candidate.page_end,
                    "run_count": candidate.run_count,
                    "sample_runs": candidate.sample_runs,
                }
                for candidate in group.chunk_candidates
            ],
        }
        for group in groups
    ]


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None

    try:
        from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
        from src.infrastructure.db.base import Base  # noqa: WPS433,F401
        from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
            __all__ as _orm_models_loaded,
        )
        from src.infrastructure.db.orm_models.document_models import (  # noqa: WPS433
            ChunkORM,
            DocumentORM,
        )
        from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
        from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433

        bootstrap_application()
        ensure_database_schema(engine)
        session = SessionLocal()

        print_status("Loading chunks...")
        query = session.query(
            ChunkORM.id,
            ChunkORM.document_id,
            ChunkORM.content,
            ChunkORM.page_start,
            ChunkORM.page_end,
        )
        if args.document_id:
            query = query.filter(ChunkORM.document_id == args.document_id)
        rows = query.all()

        if not rows:
            print("No chunks found for the given filter.")
            return 0

        print_status(f"Scanning {len(rows)} chunk(s)...")
        candidates = scan_chunk_rows(
            rows,
            min_run_length=args.min_run_length,
            min_run_count=args.min_run_count,
        )

        document_ids = {candidate.document_id for candidate in candidates}
        file_names_by_document_id: dict[str, str] = {}
        if document_ids:
            for document_id, file_name in session.query(
                DocumentORM.id, DocumentORM.file_name
            ).filter(DocumentORM.id.in_(document_ids)):
                file_names_by_document_id[document_id] = file_name

        groups = group_by_document(candidates, file_names_by_document_id)

        if args.json:
            print(json.dumps(to_json(groups), indent=2))
        else:
            print_report(groups, show_samples=args.show_samples)

        return 0

    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    raise SystemExit(main())
