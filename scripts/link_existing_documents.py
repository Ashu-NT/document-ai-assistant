from __future__ import annotations

"""
Backfill `SemanticRelationship` rows for documents that were already
extracted before `SemanticLinkingWorkflow` existed (or before
`SEMANTIC_LINKING_ENABLED` was turned on).

Unlike re-seeding with `--force-reparse`, this does not re-parse, re-extract,
or create a new document_id: it reloads each document's already-persisted
extraction entities and runs only the linking step, in place, against the
existing document_id. Safe to run repeatedly (`replace_semantic_relationships`
is a delete-then-insert keyed by document_id).

Usage:
    python scripts/link_existing_documents.py
    python scripts/link_existing_documents.py --document-id doc_001
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
            "Backfill semantic relationships for already-extracted documents, "
            "without re-parsing or re-extracting."
        )
    )
    parser.add_argument(
        "--document-id",
        help="Link only this document_id instead of every document in the corpus.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[link-existing-documents] {message}", flush=True)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None

    try:
        from src.application.services.document import DocumentCatalogService  # noqa: WPS433
        from src.application.services.extraction import ExtractionService  # noqa: WPS433
        from src.application.validation.extraction import (  # noqa: WPS433
            ExtractionResultValidator,
        )
        from src.application.workflows.linking import SemanticLinkingWorkflow  # noqa: WPS433
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
            print_status(f"Linking a single document: {args.document_id}")
        else:
            catalog_service = DocumentCatalogService(uow.documents)
            document_ids = [
                entry.document_id for entry in catalog_service.list_documents()
            ]
            if not document_ids:
                print_status("No documents found in the corpus. Nothing to link.")
                return 0
            print_status(f"Found {len(document_ids)} document(s) to link.")

        extraction_service = ExtractionService(
            extraction_repository=uow.extractions,
            extraction_result_validator=ExtractionResultValidator(),
        )
        linking_workflow = SemanticLinkingWorkflow(
            extraction_service=extraction_service,
            id_generator=IdGenerator(),
        )

        linked_count = 0
        failed_count = 0
        total_relationships = 0

        for index, document_id in enumerate(document_ids, start=1):
            prefix = f"[{index}/{len(document_ids)}]"
            try:
                relationships = linking_workflow.link(document_id)
                uow.commit()
            except ApplicationError as exc:
                uow.rollback()
                failed_count += 1
                print_status(
                    f"{prefix} FAILED to link {document_id}: {exc}"
                )
                continue

            linked_count += 1
            total_relationships += len(relationships)
            status_counts: dict[str, int] = {}
            for relationship in relationships:
                status_counts[relationship.status.value] = (
                    status_counts.get(relationship.status.value, 0) + 1
                )
            print_status(
                f"{prefix} Linked {document_id}: "
                f"{len(relationships)} relationship(s), status={status_counts}"
            )

        print_status(
            f"Done. {linked_count} document(s) linked, {failed_count} failed, "
            f"{total_relationships} relationship(s) written in total."
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
