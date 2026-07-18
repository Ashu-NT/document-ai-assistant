from __future__ import annotations

"""
Backfill `ChunkCrossReference` rows for documents that were already ingested
before `ChunkCrossReferenceLinker` existed (or before
`CHUNK_CROSS_REFERENCE_DETECTION_ENABLED` was turned on).

Unlike re-ingesting, this does not re-parse or create a new document_id: it
reloads each document's already-persisted `DocumentGraph` and runs only the
detection+resolution step against it, in place. Safe to run repeatedly
(`replace_chunk_cross_references` is a delete-then-insert keyed by
document_id).

Usage:
    python scripts/backfill_chunk_cross_references.py
    python scripts/backfill_chunk_cross_references.py --document-id doc_001
"""

import argparse
import sys
import traceback
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill chunk cross references for already-ingested documents, "
            "without re-parsing."
        )
    )
    parser.add_argument(
        "--document-id",
        help="Backfill only this document_id instead of every document in the corpus.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[backfill-chunk-cross-references] {message}", flush=True)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None

    try:
        from src.application.services.document import DocumentCatalogService  # noqa: WPS433
        from src.application.workflows.parsing.builders.document_graph.chunk_cross_reference_linker import (  # noqa: WPS433
            ChunkCrossReferenceLinker,
        )
        from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
        from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
            __all__ as _orm_models_loaded,
        )
        from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
        from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433
        from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork  # noqa: WPS433
        from src.shared.exceptions import ApplicationError  # noqa: WPS433
        from src.shared.ids import IdGenerator  # noqa: WPS433

        bootstrap_application()
        ensure_database_schema(engine)
        session = SessionLocal()
        uow = SqlAlchemyUnitOfWork(session)

        if args.document_id:
            document_ids = [args.document_id]
            print_status(f"Backfilling a single document: {args.document_id}")
        else:
            catalog_service = DocumentCatalogService(uow.documents)
            document_ids = [
                entry.document_id for entry in catalog_service.list_documents()
            ]
            if not document_ids:
                print_status("No documents found in the corpus. Nothing to backfill.")
                return 0
            print_status(f"Found {len(document_ids)} document(s) to backfill.")

        linker = ChunkCrossReferenceLinker(id_generator=IdGenerator())

        backfilled_count = 0
        failed_count = 0
        total_cross_references = 0

        for index, document_id in enumerate(document_ids, start=1):
            prefix = f"[{index}/{len(document_ids)}]"
            try:
                graph = uow.documents.get_document_graph(document_id)
                if graph is None:
                    failed_count += 1
                    print_status(f"{prefix} SKIPPED {document_id}: document not found.")
                    continue

                cross_references = linker.link(graph)
                uow.documents.replace_chunk_cross_references(
                    document_id=document_id,
                    cross_references=cross_references,
                )
                uow.commit()
            except ApplicationError as exc:
                uow.rollback()
                failed_count += 1
                print_status(f"{prefix} FAILED to backfill {document_id}: {exc}")
                continue

            backfilled_count += 1
            total_cross_references += len(cross_references)
            status_counts: dict[str, int] = {}
            for cross_reference in cross_references:
                key = f"{cross_reference.reference_type.value}:{cross_reference.resolution_status.value}"
                status_counts[key] = status_counts.get(key, 0) + 1
            print_status(
                f"{prefix} Backfilled {document_id}: "
                f"{len(cross_references)} cross reference(s), status={status_counts}"
            )

        print_status(
            f"Done. {backfilled_count} document(s) backfilled, {failed_count} failed, "
            f"{total_cross_references} cross reference(s) written in total."
        )
        return 1 if failed_count else 0

    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    raise SystemExit(main())
