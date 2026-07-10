from __future__ import annotations

"""
Debug tool: print RAW results from each of the three retrieval sources -
dense (Qdrant), sparse/keyword (SQL), and semantics (structured entities +
their SemanticRelationship links, SQL) - as three clearly separate
sections, then what survives after each source's resolution step.

There is no single unified "resolver" across all three sources in this
codebase; there are two independent resolve steps:
  - chunks (dense + keyword): `HybridRetrievalService` fuses the two raw
    result lists via Reciprocal Rank Fusion (RRF), then optionally
    reranks and truncates to top_k.
  - semantics: when --document-id is given, every structured entity type
    is listed directly for that document (no question-based detection),
    each entity's `related_entities` (its SemanticRelationship links) is
    printed alongside it, and the combined raw list is deduplicated via
    `deduplicate_structured_entities()`. Without --document-id, falls back
    to the question-driven `resolve_structured_entities()` path (detects
    an entity type from the question text) since an un-scoped dump across
    the whole corpus would be unbounded.

Usage:
    # 1. Find a real, FULL document_id first - the plain table view from
    #    list_documents.py truncates IDs (e.g. "doc_69a27352abea4..."),
    #    which is not a valid id and will make every section return 0:
    #        python scripts/list_documents.py --json
    #
    # 2. Run with that full id (verified working example against this
    #    repo's seeded corpus - swap in your own document_id/question):
    #        python scripts/debug_retrieval_resolution.py "maintenance interval for the filter" --document-id doc_69a27352abea478c892e066198609957 --top-k 3
    #
    # 3. Narrow the semantics section to one entity type:
    #        python scripts/debug_retrieval_resolution.py "filter" --document-id doc_001 --entity-type spare_part
    #
    # 4. No --document-id: falls back to question-text entity detection
    #    instead of a full per-document semantics dump:
    #        python scripts/debug_retrieval_resolution.py "What is the pressure rating?"
    #
    # If semantics still returns 0 with a correct, full document_id:
    #   - 0 entities of EVERY type -> that document was never extracted
    #     (or extraction failed for it) - nothing for linking to work with.
    #   - entities show up but no "->" relationship lines under any of them
    #     -> extraction succeeded but SemanticLinkingWorkflow never ran for
    #     it (SEMANTIC_LINKING_ENABLED was off, or it predates that
    #     feature). Backfill it directly:
    #        python scripts/link_existing_documents.py --document-id doc_69a27352abea478c892e066198609957
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

from src.shared.text import console_safe_text


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
        help=(
            "Optional document_id to scope retrieval to. Also switches the "
            "semantics section to a full per-document dump across all "
            "entity types (or --entity-type, if given) instead of "
            "question-based detection."
        ),
    )
    parser.add_argument(
        "--entity-type",
        default=None,
        help=(
            "Restrict the semantics section to this one structured entity "
            "type (e.g. spare_part, maintenance_task, procedure). Only "
            "used together with --document-id; ignored otherwise."
        ),
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="top_k for the final reranked/truncated chunk result, and per "
        "entity-type cap in the semantics section.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(console_safe_text(f"[debug-retrieval] {message}"), flush=True)


def print_section(title: str) -> None:
    banner = "=" * 70
    print()
    print(console_safe_text(banner))
    print(console_safe_text(f"  {title}"))
    print(console_safe_text(banner))


def print_chunks(label: str, chunks: list) -> None:
    print_status(f"{label} ({len(chunks)} chunk(s))")
    for index, chunk in enumerate(chunks, start=1):
        preview = " ".join(chunk.content.split())
        if len(preview) > 160:
            preview = preview[:157] + "..."
        print(
            console_safe_text(
                f"  [{index}] chunk_id={chunk.chunk_id} document_id={chunk.document_id} "
                f"score={chunk.score:.4f} source={chunk.retrieval_source} "
                f"chunk_type={chunk.chunk_type.value} "
                f"section={'/'.join(chunk.section_path) or '-'}"
            )
        )
        print(console_safe_text(f"      {preview}"))


# entity_type -> (id_field, fields worth showing inline to identify the row)
_ENTITY_SUMMARY_FIELDS: dict[str, tuple[str, tuple[str, ...]]] = {
    "manufacturer": ("manufacturer_id", ("name", "website", "country")),
    "supplier": ("supplier_id", ("name", "website", "country")),
    "spare_part": ("spare_part_id", ("part_number", "description", "quantity")),
    "equipment": ("equipment_id", ("name", "model_number", "manufacturer_name")),
    "maintenance_task": ("task_id", ("title", "interval", "component_name")),
    "procedure": ("procedure_id", ("title", "procedure_type", "steps")),
    "specification": ("specification_id", ("parameter", "value", "unit")),
    "safety_warning": ("safety_warning_id", ("warning_type", "message")),
    "maintenance_interval": (
        "maintenance_interval_id",
        ("interval", "component_name"),
    ),
    "troubleshooting": ("troubleshooting_id", ("symptom", "cause")),
}


def _format_field_value(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        numbered = "; ".join(f"{i}. {step}" for i, step in enumerate(value, start=1))
        return f"[{numbered}]"
    return repr(value)


def _summarize_entity(entity: dict[str, Any]) -> str:
    entity_type = entity.get("_entity_type") or entity.get("entity_type") or "?"
    id_field, label_fields = _ENTITY_SUMMARY_FIELDS.get(entity_type, (None, ()))
    entity_id = entity.get(id_field, "?") if id_field else "?"
    labels = ", ".join(
        f"{field}={_format_field_value(entity[field])}"
        for field in label_fields
        if entity.get(field) not in (None, "", [])
    )
    confidence = entity.get("confidence_score")
    review = entity.get("requires_human_review")
    return (
        f"{entity_type}:{entity_id}"
        + (f" [{labels}]" if labels else "")
        + f" (confidence={confidence}, needs_review={review})"
    )


def print_entities(label: str, entities: list[dict[str, Any]]) -> None:
    noun = "entity" if len(entities) == 1 else "entities"
    print_status(f"{label} ({len(entities)} {noun})")
    for index, entity in enumerate(entities, start=1):
        print(console_safe_text(f"  [{index}] {_summarize_entity(entity)}"))
        for link in entity.get("related_entities") or []:
            related_entity = link.get("entity")
            related_summary = (
                _summarize_entity({**related_entity, "_entity_type": link["entity_type"]})
                if related_entity
                else "(not found)"
            )
            print(
                console_safe_text(
                    f"      -> {link['relationship_type']} ({link['direction']}, "
                    f"status={link['status']}, "
                    f"confidence={link['confidence_score']:.2f}): {related_summary}"
                )
            )


def collect_document_semantics(
    tool: Any,
    *,
    document_id: str,
    entity_type: str | None,
    top_k: int,
) -> list[dict[str, Any]]:
    """List structured entities (with their `related_entities` semantic
    links) directly for a document, bypassing the narrow question-text
    detector entirely - one or all entity types, whichever is asked for."""
    from src.application.tools.retrieval.retrieve_structured_entities_tool import (
        RetrieveStructuredEntitiesRequest,
        StructuredEntityType,
    )

    entity_types = (
        [StructuredEntityType(entity_type)]
        if entity_type
        else list(StructuredEntityType)
    )

    raw_entities: list[dict[str, Any]] = []
    for candidate_type in entity_types:
        result = tool.run(
            RetrieveStructuredEntitiesRequest(
                entity_type=candidate_type.value,
                document_id=document_id,
                top_k=top_k,
            )
        )
        if not result.success or not isinstance(result.data, dict):
            continue
        items = result.data.get("items") or []
        raw_entities.extend(
            {**item, "_entity_type": candidate_type.value}
            for item in items
            if isinstance(item, dict)
        )
    return raw_entities


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
        print_status(
            f"document_id={args.document_id!r} entity_type={args.entity_type!r} "
            f"top_k={args.top_k}"
        )

        extraction_service = ExtractionService(
            extraction_repository=uow.extractions,
            extraction_result_validator=ExtractionResultValidator(),
        )
        structured_entities_tool = RetrieveStructuredEntitiesTool(extraction_service)

        # --- 1. Semantics: structured entities + their SemanticRelationship links ---
        print_section("SEMANTICS (structured entities + semantic links)")
        if args.document_id:
            raw_entities = collect_document_semantics(
                structured_entities_tool,
                document_id=args.document_id,
                entity_type=args.entity_type,
                top_k=args.top_k,
            )
            print_entities(
                f"RAW semantics for document_id={args.document_id!r}"
                + (f" (entity_type={args.entity_type!r})" if args.entity_type else ""),
                raw_entities,
            )
        else:
            tool_registry = ToolRegistry(
                retrieve_structured_entities_tool=structured_entities_tool
            )
            detected_entity_type = detect_structured_entity_type(args.question)
            print_status(
                "No --document-id given: falling back to question-based "
                f"detection. Detected structured entity type: {detected_entity_type!r}"
            )
            raw_entities = resolve_structured_entities(
                tool_registry,
                question=args.question,
                document_id=args.document_id,
            )
            print_entities("RAW semantics (question-detected)", raw_entities)

        deduped_entities = deduplicate_structured_entities(raw_entities)
        print_entities(
            "AFTER RESOLUTION: deduplicated semantics", deduped_entities
        )

        # --- 2. Sparse (keyword/SQL) chunks, raw ---
        print_section("SPARSE (SQL keyword) chunks")
        source_results = retrieval_service._collect_source_results(query)
        sparse_chunks = next(
            (chunks for name, chunks in source_results if name == "sql_keyword"), []
        )
        print_chunks("RAW sparse (SQL keyword)", sparse_chunks)

        # --- 3. Dense (Qdrant) chunks, raw ---
        print_section("DENSE (Qdrant) chunks")
        dense_chunks = next(
            (chunks for name, chunks in source_results if name == "dense"), []
        )
        print_chunks("RAW dense (Qdrant)", dense_chunks)

        # --- Chunk resolution: RRF fusion of the two sources above, then rerank ---
        # `_collect_source_results`/`_fuse_results` are internal methods;
        # reaching into them here is intentional so this script sees the
        # exact same intermediate state production code produces.
        print_section("CHUNK RESOLUTION (sparse + dense fused)")
        fused = retrieval_service._fuse_results(source_results)
        print_chunks(
            "AFTER RESOLUTION: fused chunks (RRF), pre-rerank/top_k", fused
        )

        final_result = retrieval_service.retrieve(query)
        print_chunks(
            f"AFTER RESOLUTION: final chunks (reranked, top_k={args.top_k})",
            final_result.chunks,
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
