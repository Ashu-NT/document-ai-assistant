from __future__ import annotations

"""
List all documents stored in the document corpus (SQLite).

Usage:
    python scripts/list_documents.py
    python scripts/list_documents.py --json
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
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List all documents stored in the document corpus."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[list-documents] {message}", flush=True)


def _trunc(value: str | None, max_len: int, placeholder: str = "-") -> str:
    if value is None:
        return placeholder
    if len(value) <= max_len:
        return value
    return value[: max_len - 3] + "..."


def fetch_documents(session) -> list:
    from sqlalchemy import func, select  # noqa: WPS433

    from src.infrastructure.db.orm_models import ChunkORM, DocumentORM  # noqa: WPS433

    chunk_count_subq = (
        select(func.count(ChunkORM.id))
        .where(ChunkORM.document_id == DocumentORM.id)
        .correlate(DocumentORM)
        .scalar_subquery()
    )
    stmt = (
        select(DocumentORM, chunk_count_subq.label("chunk_count"))
        .order_by(DocumentORM.created_at.desc())
    )
    return session.execute(stmt).all()


def print_table(rows: list) -> None:
    w_id, w_title, w_file, w_type, w_pages, w_chunks = 20, 30, 28, 12, 5, 6

    header = (
        f"{'ID':<{w_id}}  {'Title':<{w_title}}  {'File Name':<{w_file}}  "
        f"{'Type':<{w_type}}  {'Pages':>{w_pages}}  {'Chunks':>{w_chunks}}  Ingested"
    )
    print(header)
    print("-" * len(header))

    for doc, chunk_count in rows:
        pages = str(doc.page_count) if doc.page_count is not None else "-"
        chunks = str(chunk_count if chunk_count is not None else 0)
        created = (
            doc.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if doc.created_at is not None
            else "-"
        )
        print(
            f"{_trunc(doc.id, w_id):<{w_id}}  "
            f"{_trunc(doc.title, w_title):<{w_title}}  "
            f"{_trunc(doc.file_name, w_file):<{w_file}}  "
            f"{_trunc(doc.document_type, w_type):<{w_type}}  "
            f"{pages:>{w_pages}}  "
            f"{chunks:>{w_chunks}}  "
            f"{created}"
        )


def to_json_records(rows: list) -> list[dict[str, Any]]:
    return [
        {
            "document_id": doc.id,
            "title": doc.title,
            "file_name": doc.file_name,
            "document_type": doc.document_type,
            "page_count": doc.page_count,
            "chunk_count": chunk_count or 0,
            "ingested_at": (
                doc.created_at.isoformat() if doc.created_at is not None else None
            ),
        }
        for doc, chunk_count in rows
    ]


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None

    try:
        from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
        from src.infrastructure.db.base import Base  # noqa: WPS433
        from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
            __all__ as _orm_models_loaded,
        )
        from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433

        bootstrap_application()
        Base.metadata.create_all(engine)
        session = SessionLocal()

        rows = fetch_documents(session)

        if not rows:
            print("No documents found in the corpus.")
            print(
                "Seed documents first: "
                "python scripts/seed_retrieval_benchmark_corpus.py"
            )
            return 0

        if args.json:
            print(json.dumps(to_json_records(rows), indent=2))
        else:
            print(f"Found {len(rows)} document(s).\n")
            print_table(rows)

        return 0

    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    raise SystemExit(main())
