from __future__ import annotations

"""
Audit and optionally delete duplicate documents from the local corpus.

Default behavior is a dry run that keeps the oldest document in each duplicate
group and marks newer ones for deletion.

Usage:
    python scripts/cleanup_duplicate_documents.py
    python scripts/cleanup_duplicate_documents.py --apply
    python scripts/cleanup_duplicate_documents.py --group-by file_name --apply
    python scripts/cleanup_duplicate_documents.py --filter FWC12 --json
"""

import argparse
import json
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Sequence

from sqlalchemy import func, or_, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

GroupBy = Literal["file_path", "file_name", "file_hash", "content_hash"]
KeepPolicy = Literal["oldest", "newest"]


@dataclass(slots=True, frozen=True)
class DuplicateDocumentRecord:
    document_id: str
    title: str | None
    file_name: str
    file_path: str
    file_hash: str
    content_hash: str | None
    document_type: str
    page_count: int | None
    chunk_count: int
    created_at: datetime | None


@dataclass(slots=True, frozen=True)
class DuplicateDeletionPlan:
    group_key: str
    keep_record: DuplicateDocumentRecord
    delete_records: tuple[DuplicateDocumentRecord, ...]
    warning: str | None = None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit duplicate documents and optionally delete the newer copies."
        )
    )
    parser.add_argument(
        "--group-by",
        choices=["file_path", "file_name", "file_hash", "content_hash"],
        default="file_path",
        help="Field used to detect duplicate groups. Default: file_path.",
    )
    parser.add_argument(
        "--keep",
        choices=["oldest", "newest"],
        default="oldest",
        help="Which document in each duplicate group to keep. Default: oldest.",
    )
    parser.add_argument(
        "--filter",
        help="Optional case-insensitive substring filter on title, file name, or file path.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete the duplicate documents marked by the plan.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the duplicate plan as JSON instead of a text table.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[cleanup-duplicate-documents] {message}", flush=True)


def build_duplicate_deletion_plans(
    records: Sequence[DuplicateDocumentRecord],
    *,
    group_by: GroupBy,
    keep: KeepPolicy,
) -> list[DuplicateDeletionPlan]:
    grouped: dict[str, list[DuplicateDocumentRecord]] = {}
    for record in records:
        group_key = getattr(record, group_by)
        if group_key is None:
            continue
        normalized_key = str(group_key).strip()
        if not normalized_key:
            continue
        grouped.setdefault(normalized_key, []).append(record)

    plans: list[DuplicateDeletionPlan] = []
    for group_key, group_records in sorted(grouped.items()):
        if len(group_records) < 2:
            continue

        sorted_records = sorted(
            group_records,
            key=lambda item: _sort_key(item, keep=keep),
        )
        keep_record = sorted_records[0]
        delete_records = tuple(sorted_records[1:])
        warning = _build_plan_warning(keep_record, delete_records)
        plans.append(
            DuplicateDeletionPlan(
                group_key=group_key,
                keep_record=keep_record,
                delete_records=delete_records,
                warning=warning,
            )
        )
    return plans


def _sort_key(
    record: DuplicateDocumentRecord,
    *,
    keep: KeepPolicy,
) -> tuple[datetime, str]:
    if keep == "oldest":
        created_at = record.created_at or datetime.max
        return (created_at, record.document_id)

    created_at = record.created_at or datetime.min
    return (-created_at.timestamp() if record.created_at else float("-inf"), record.document_id)


def _build_plan_warning(
    keep_record: DuplicateDocumentRecord,
    delete_records: Sequence[DuplicateDocumentRecord],
) -> str | None:
    max_deleted_chunk_count = max(
        (record.chunk_count for record in delete_records),
        default=keep_record.chunk_count,
    )
    if keep_record.chunk_count < max_deleted_chunk_count:
        return (
            "keep candidate has fewer chunks than a newer duplicate; review "
            "before applying if you expect the newest copy to be the richer one"
        )
    return None


def format_plans_as_json(plans: Sequence[DuplicateDeletionPlan]) -> str:
    payload = []
    for plan in plans:
        payload.append(
            {
                "group_key": plan.group_key,
                "keep_record": _record_to_dict(plan.keep_record),
                "delete_records": [
                    _record_to_dict(record) for record in plan.delete_records
                ],
                "warning": plan.warning,
            }
        )
    return json.dumps(payload, indent=2)


def print_plans(plans: Sequence[DuplicateDeletionPlan], *, group_by: GroupBy) -> None:
    if not plans:
        print("No duplicate groups found.")
        return

    total_delete_candidates = sum(len(plan.delete_records) for plan in plans)
    print(
        f"Found {len(plans)} duplicate group(s) using `{group_by}`; "
        f"{total_delete_candidates} document(s) would be deleted.\n"
    )

    for index, plan in enumerate(plans, start=1):
        print(f"[{index}] {group_by} = {plan.group_key}")
        print(f"    keep   {format_record(plan.keep_record)}")
        for record in plan.delete_records:
            print(f"    delete {format_record(record)}")
        if plan.warning:
            print(f"    warning {plan.warning}")
        print()


def format_record(record: DuplicateDocumentRecord) -> str:
    created_at = record.created_at.isoformat(sep=" ", timespec="seconds") if record.created_at else "-"
    title = record.title or "-"
    short_id = record.document_id[:12]
    return (
        f"{short_id} | title={title} | file={record.file_name} | "
        f"chunks={record.chunk_count} | created_at={created_at}"
    )


def load_document_records(
    *,
    filter_text: str | None = None,
) -> list[DuplicateDocumentRecord]:
    from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
    from src.infrastructure.db.orm_models import ChunkORM, DocumentORM  # noqa: WPS433
    from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
    from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433

    bootstrap_application()
    ensure_database_schema(engine)

    chunk_count = (
        select(func.count(ChunkORM.id))
        .where(ChunkORM.document_id == DocumentORM.id)
        .correlate(DocumentORM)
        .scalar_subquery()
    )
    statement = select(
        DocumentORM.id,
        DocumentORM.title,
        DocumentORM.file_name,
        DocumentORM.file_path,
        DocumentORM.file_hash,
        DocumentORM.content_hash,
        DocumentORM.document_type,
        DocumentORM.page_count,
        DocumentORM.created_at,
        chunk_count.label("chunk_count"),
    ).order_by(DocumentORM.created_at.asc(), DocumentORM.id.asc())

    if filter_text:
        pattern = f"%{filter_text.strip()}%"
        statement = statement.where(
            or_(
                DocumentORM.title.ilike(pattern),
                DocumentORM.file_name.ilike(pattern),
                DocumentORM.file_path.ilike(pattern),
            )
        )

    session = SessionLocal()
    try:
        rows = session.execute(statement).all()
        return [
            DuplicateDocumentRecord(
                document_id=row.id,
                title=row.title,
                file_name=row.file_name,
                file_path=row.file_path,
                file_hash=row.file_hash,
                content_hash=row.content_hash,
                document_type=row.document_type,
                page_count=row.page_count,
                chunk_count=int(row.chunk_count or 0),
                created_at=row.created_at,
            )
            for row in rows
        ]
    finally:
        session.close()


def apply_deletion_plans(plans: Sequence[DuplicateDeletionPlan]) -> tuple[int, list[str]]:
    from src.application.orchestrator.ingestion.ingestion_orchestrator import (  # noqa: WPS433
        build_ingestion_runtime,
    )

    runtime = build_ingestion_runtime(bootstrap=True)
    deleted_count = 0
    failures: list[str] = []
    try:
        delete_candidates = [
            record
            for plan in plans
            for record in plan.delete_records
        ]
        for index, record in enumerate(delete_candidates, start=1):
            try:
                print_status(
                    f"[{index}/{len(delete_candidates)}] Deleting {record.document_id} "
                    f"({record.file_name})..."
                )
                runtime.delete_document_workflow.run(record.document_id)
                deleted_count += 1
            except Exception as exc:
                failures.append(f"{record.document_id}: {exc}")
        return deleted_count, failures
    finally:
        runtime.close()


def _record_to_dict(record: DuplicateDocumentRecord) -> dict[str, Any]:
    payload = asdict(record)
    payload["created_at"] = (
        record.created_at.isoformat() if record.created_at is not None else None
    )
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        print_status("Loading document inventory...")
        records = load_document_records(filter_text=args.filter)
        plans = build_duplicate_deletion_plans(
            records,
            group_by=args.group_by,
            keep=args.keep,
        )

        if args.json:
            print(format_plans_as_json(plans))
        else:
            print_plans(plans, group_by=args.group_by)

        if not args.apply:
            print_status("Dry run only. Re-run with --apply to delete the marked documents.")
            return 0

        if not plans:
            print_status("Nothing to delete.")
            return 0

        deleted_count, failures = apply_deletion_plans(plans)
        print_status(f"Deleted {deleted_count} duplicate document(s).")
        if failures:
            print_status("Some deletions failed:")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        return 0

    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
