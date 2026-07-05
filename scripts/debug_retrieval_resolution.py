from __future__ import annotations

"""
Debug tool: for a given question, print the RAW results from each of the
three retrieval sources - dense (Qdrant), sparse/keyword (SQL), and
structured entities (SQL) - and what survives after resolution.

There is no single unified "resolver" across all three sources in this
codebase; there are two independent resolve steps:
  - chunks (dense + keyword): `HybridRetrievalService` fuses the two raw
    result lists via Reciprocal Rank Fusion (RRF), then optionally
    reranks and truncates to top_k.
  - structured entities: `resolve_structured_entities()` detects an
    entity type from the question text and queries it, then
    `deduplicate_structured_entities()` drops duplicate rows.
This script surfaces both "before" states and both "after" states so you
can see exactly what each resolution step changed.

Usage:
    python scripts/debug_retrieval_resolution.py "What is the pressure rating?"
    python scripts/debug_retrieval_resolution.py "..." --document-id doc_001 --top-k 5
"""

import argparse
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
        description=(
            "Show raw per-source retrieval results and what survives after "
            "each source's resolution step."
        )
    )
    parser.add_argument("question", help="The question/query text to retrieve for.")
    parser.add_argument(
        "--document-id",
        default=None,
        help="Optional document_id to scope retrieval to.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="top_k for the final reranked/truncated chunk result.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _console_safe_text(value: str) -> str:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return value.encode(encoding, errors="replace").decode(encoding, errors="replace")
    except LookupError:
        return value.encode("utf-8", errors="replace").decode("utf-8", errors="replace")


def print_status(message: str) -> None:
    print(_console_safe_text(f"[debug-retrieval] {message}"), flush=True)


def print_chunks(label: str, chunks: list) -> None:
    print_status(f"{label} ({len(chunks)} chunk(s))")
    for index, chunk in enumerate(chunks, start=1):
        preview = " ".join(chunk.content.split())
        if len(preview) > 160:
            preview = preview[:157] + "..."
        print(
            _console_safe_text(
                f"  [{index}] chunk_id={chunk.chunk_id} document_id={chunk.document_id} "
                f"score={chunk.score:.4f} source={chunk.retrieval_source} "
                f"chunk_type={chunk.chunk_type.value} "
                f"section={'/'.join(chunk.section_path) or '-'}"
            )
        )
        print(_console_safe_text(f"      {preview}"))


def print_entities(label: str, entities: list[dict[str, Any]]) -> None:
    noun = "entity" if len(entities) == 1 else "entities"
    print_status(f"{label} ({len(entities)} {noun})")
    for index, entity in enumerate(entities, start=1):
        entity_type = entity.get("_entity_type", "?")
        fields = {
            key: value
            for key, value in entity.items()
            if key not in {"_entity_type", "audit"}
        }
        print(_console_safe_text(f"  [{index}] entity_type={entity_type} {fields}"))


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None
    qdrant_client = None

    try:
        from src.application.langgraph.common import detect_structured_entity_type
        from src.application.langgraph.factories.tool_registry import ToolRegistry
        from src.application.langgraph.nodes.node_utils import (
            deduplicate_structured_entities,
            resolve_structured_entities,
        )
        from src.application.orchestrator.retrieval import build_retrieval_runtime
        from src.application.services.extraction import ExtractionService
        from src.application.tools.retrieval.retrieve_structured_entities_tool import (
            RetrieveStructuredEntitiesTool,
        )
        from src.application.validation.extraction import ExtractionResultValidator
        from src.bootstrap.startup import bootstrap_application
        from src.domain.retrieval import RetrievalQuery
        from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded  # noqa: F401
        from src.infrastructure.db.schema_management import ensure_database_schema
        from src.infrastructure.db.session import SessionLocal, engine
        from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
        from src.shared.ids import IdGenerator

        bootstrap_application()
        ensure_database_schema(engine)
        session = SessionLocal()
        uow = SqlAlchemyUnitOfWork(session)

        retrieval_runtime = build_retrieval_runtime(unit_of_work=uow)
        qdrant_client = retrieval_runtime.qdrant_client
        # Reuse the exact service instance `RetrievalWorkflow` runs in
        # production, so this inspects real wiring rather than a
        # hand-rebuilt copy that could drift from it.
        retrieval_service = retrieval_runtime.retrieval_workflow.retrieval_service

        query = RetrievalQuery(
            query_id=IdGenerator().new_retrieval_id(),
            query_text=args.question,
            document_id=args.document_id,
            top_k=args.top_k,
        )

        print_status(f"Question: {args.question!r}")
        print_status(f"document_id={args.document_id!r} top_k={args.top_k}")

        # --- Chunks: raw per-source, then resolved (RRF fusion + rerank) ---
        # `_collect_source_results`/`_fuse_results` are internal methods;
        # reaching into them here is intentional so this script sees the
        # exact same intermediate state production code produces.
        source_results = retrieval_service._collect_source_results(query)
        for source_name, chunks in source_results:
            print_chunks(f"RAW [{source_name}]", chunks)

        fused = retrieval_service._fuse_results(source_results)
        print_chunks(
            "AFTER RESOLUTION: fused chunks (RRF), pre-rerank/top_k", fused
        )

        final_result = retrieval_service.retrieve(query)
        print_chunks(
            f"AFTER RESOLUTION: final chunks (reranked, top_k={args.top_k})",
            final_result.chunks,
        )

        # --- Structured entities: raw, then deduplicated ---
        extraction_service = ExtractionService(
            extraction_repository=uow.extractions,
            extraction_result_validator=ExtractionResultValidator(),
        )
        structured_entities_tool = RetrieveStructuredEntitiesTool(extraction_service)
        tool_registry = ToolRegistry(
            retrieve_structured_entities_tool=structured_entities_tool
        )

        detected_entity_type = detect_structured_entity_type(args.question)
        print_status(f"Detected structured entity type: {detected_entity_type!r}")

        raw_entities = resolve_structured_entities(
            tool_registry,
            question=args.question,
            document_id=args.document_id,
        )
        print_entities("RAW structured entities", raw_entities)

        deduped_entities = deduplicate_structured_entities(raw_entities)
        print_entities(
            "AFTER RESOLUTION: deduplicated structured entities", deduped_entities
        )

        return 0

    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if session is not None:
            session.close()
        close_quietly(qdrant_client)


def close_quietly(resource) -> None:
    if resource is None:
        return
    close = getattr(resource, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            return


if __name__ == "__main__":
    raise SystemExit(main())
