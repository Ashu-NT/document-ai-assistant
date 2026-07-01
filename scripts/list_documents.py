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


def print_table(rows: list[dict[str, Any]]) -> None:
    w_id, w_title, w_file, w_type, w_pages, w_chunks = 20, 30, 28, 12, 5, 6

    header = (
        f"{'ID':<{w_id}}  {'Title':<{w_title}}  {'File Name':<{w_file}}  "
        f"{'Type':<{w_type}}  {'Pages':>{w_pages}}  {'Chunks':>{w_chunks}}  Ingested"
    )
    print(header)
    print("-" * len(header))

    for row in rows:
        pages = str(row["page_count"]) if row["page_count"] is not None else "-"
        chunks = str(row["chunk_count"])
        created = row["ingested_at"] or "-"
        print(
            f"{_trunc(row['document_id'], w_id):<{w_id}}  "
            f"{_trunc(row['title'], w_title):<{w_title}}  "
            f"{_trunc(row['file_name'], w_file):<{w_file}}  "
            f"{_trunc(row['document_type'], w_type):<{w_type}}  "
            f"{pages:>{w_pages}}  "
            f"{chunks:>{w_chunks}}  "
            f"{created}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None

    try:
        from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
        from src.infrastructure.db.base import Base  # noqa: WPS433
        from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
        from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
            __all__ as _orm_models_loaded,
        )
        from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433

        bootstrap_application()
        ensure_database_schema(engine)
        session = SessionLocal()
        from src.application.services.document import DocumentCatalogService  # noqa: WPS433
        from src.application.tools.documents import (  # noqa: WPS433
            ListDocumentsRequest,
            ListDocumentsTool,
        )
        from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork  # noqa: WPS433

        uow = SqlAlchemyUnitOfWork(session)
        tool = ListDocumentsTool(DocumentCatalogService(uow.documents))
        result = tool.run(ListDocumentsRequest())
        if not result.success:
            print(result.message or "Failed to list documents.", file=sys.stderr)
            return 1

        rows = result.data or []

        if not rows:
            print("No documents found in the corpus.")
            print(
                "Seed documents first: "
                "python scripts/seed_retrieval_benchmark_corpus.py"
            )
            return 0

        if args.json:
            print(json.dumps(rows, indent=2))
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
