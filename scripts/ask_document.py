from __future__ import annotations

"""
Ask a question against documents already seeded in the corpus.

Usage:
    python scripts/ask_document.py "What is the oil change interval?" --latest
    python scripts/ask_document.py --question "..." --document "Engine Manual" --generate
    python scripts/ask_document.py --help
"""

import argparse
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)


@dataclass(slots=True)
class QARuntime:
    workflow: Any
    session: Any = None
    qdrant_client: Any = None
    # Non-None when AnswerGenerationService was wired; holds the resolved model name.
    generation_model: str | None = None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask a question against documents already seeded in the corpus.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/ask_document.py 'What is the maintenance interval?' --latest\n"
            "  python scripts/ask_document.py --question '...' --document 'Engine Manual' --generate\n"
            "  python scripts/ask_document.py --question '...' --document-id abc123 --show-context\n"
        ),
    )
    parser.add_argument(
        "question_positional",
        nargs="?",
        metavar="QUESTION",
        help="The question to ask (positional).",
    )
    parser.add_argument(
        "--question",
        "-q",
        help="The question to ask (flag form).",
    )

    doc_group = parser.add_mutually_exclusive_group()
    doc_group.add_argument(
        "--document-id",
        metavar="ID",
        help="Target a specific document by its ID.",
    )
    doc_group.add_argument(
        "--document",
        "-d",
        metavar="NAME",
        help="Find a document by title or filename (partial, case-insensitive).",
    )
    doc_group.add_argument(
        "--latest",
        action="store_true",
        help="Use the most recently ingested document.",
    )

    parser.add_argument(
        "--generate",
        action="store_true",
        help="Enable answer generation via LLM (requires Ollama).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        metavar="N",
        help="Number of chunks to retrieve (default: workflow default).",
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Show retrieved context chunks with approved/rejected status.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Write a retrieval trace JSON to outputs/debug_retrieval/.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[ask-document] {message}", flush=True)


def resolve_question(args: argparse.Namespace) -> str | None:
    return args.question or args.question_positional


def _trunc(value: str | None, max_len: int) -> str:
    if value is None:
        return "-"
    if len(value) <= max_len:
        return value
    return value[: max_len - 3] + "..."


def _page_range(source) -> str:
    start = getattr(source, "page_start", None)
    end = getattr(source, "page_end", None)
    if start is None:
        return ""
    if end is not None and end != start:
        return f"pages {start}-{end}"
    return f"page {start}"


def resolve_document(session, args: argparse.Namespace) -> tuple[str | None, str | None]:
    """Returns (document_id, display_name) or (None, None) if not found / no selector."""
    from sqlalchemy import select  # noqa: WPS433

    from src.infrastructure.db.orm_models import DocumentORM  # noqa: WPS433

    if args.document_id:
        stmt = select(DocumentORM).where(DocumentORM.id == args.document_id)
        doc = session.execute(stmt).scalar_one_or_none()
        if doc is None:
            print(f"Document ID not found: {args.document_id}", file=sys.stderr)
            return None, None
        return doc.id, doc.title or doc.file_name

    if args.document:
        pattern = f"%{args.document}%"
        stmt = (
            select(DocumentORM)
            .where(
                DocumentORM.title.ilike(pattern) | DocumentORM.file_name.ilike(pattern)
            )
            .order_by(DocumentORM.created_at.desc())
        )
        matches = session.execute(stmt).scalars().all()
        if not matches:
            print(f'No document found matching "{args.document}".', file=sys.stderr)
            return None, None
        if len(matches) > 1:
            print(
                f'Multiple documents match "{args.document}" — be more specific:',
                file=sys.stderr,
            )
            for m in matches:
                print(f"  {m.id[:20]}  {m.title or m.file_name}", file=sys.stderr)
            return None, None
        doc = matches[0]
        return doc.id, doc.title or doc.file_name

    if args.latest:
        stmt = select(DocumentORM).order_by(DocumentORM.created_at.desc()).limit(1)
        doc = session.execute(stmt).scalar_one_or_none()
        if doc is None:
            print("No documents found in the corpus.", file=sys.stderr)
            return None, None
        return doc.id, doc.title or doc.file_name

    return None, None


def _create_qdrant_client(qdrant_client_class):
    from src.config.settings import qdrant_settings  # noqa: WPS433

    if qdrant_settings.mode.lower() == "local":
        return qdrant_client_class(path=str(qdrant_settings.storage_path))
    return qdrant_client_class(host=qdrant_settings.host, port=qdrant_settings.port)


def build_qa_runtime(session, *, enable_generation: bool) -> QARuntime:
    from qdrant_client import QdrantClient  # noqa: WPS433

    from src.application.guardrails.answering import (  # noqa: WPS433
        AnswerSupportGuardrail,
        CitationGuardrail,
        SafetyAnswerGuardrail,
        UnsupportedClaimGuardrail,
        UnsupportedSuggestionGuardrail,
    )
    from src.application.guardrails.context import (  # noqa: WPS433
        ContextBudgetGuardrail,
        ContextFilteringGuardrail,
        ContextQualityGuardrail,
    )
    from src.application.guardrails.retrieval import (  # noqa: WPS433
        DocumentRelevanceGuardrail,
        RetrievalEvidenceGuardrail,
    )
    from src.application.services.ai import LLMService  # noqa: WPS433
    from src.application.services.answer_generation import (  # noqa: WPS433
        AnswerGenerationService,
    )
    from src.application.services.document import DocumentLookupService  # noqa: WPS433
    from src.application.services.document_exploration import (  # noqa: WPS433
        DocumentExplorationService,
    )
    from src.application.services.retrieval import HybridRetrievalService  # noqa: WPS433
    from src.application.validation.retrieval import (  # noqa: WPS433
        RetrievalQueryValidator,
    )
    from src.application.workflows.question_answering import (  # noqa: WPS433
        QuestionAnsweringRouter,
        QuestionAnsweringWorkflow,
    )
    from src.application.workflows.retrieval import (  # noqa: WPS433
        RetrievalContextExpander,
        RetrievalWorkflow,
    )
    from src.config.settings import (  # noqa: WPS433
        embedding_settings,
        llm_settings,
        qdrant_settings,
    )
    from src.infrastructure.ai.embeddings import BgeEmbeddingProvider  # noqa: WPS433
    from src.infrastructure.ai.llm import OllamaLLMProvider  # noqa: WPS433
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork  # noqa: WPS433
    from src.infrastructure.retrieval.keyword import SqlKeywordIndex  # noqa: WPS433
    from src.infrastructure.retrieval.rerankers import (  # noqa: WPS433
        DeterministicHybridReranker,
    )
    from src.infrastructure.retrieval.vector import QdrantVectorStore  # noqa: WPS433
    from src.shared.ids import IdGenerator  # noqa: WPS433

    uow = SqlAlchemyUnitOfWork(session)
    query_validator = RetrievalQueryValidator()
    embedding_provider = BgeEmbeddingProvider(model_name=embedding_settings.model_name)
    qdrant_client = _create_qdrant_client(QdrantClient)

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        mapping_repository=uow.vector_mappings,
        collection_name=qdrant_settings.collection,
        embedding_model=embedding_settings.model_name,
        query_embedding_provider=embedding_provider,
        document_repository=uow.documents,
    )
    document_lookup_service = DocumentLookupService(uow.documents)
    retrieval_service = HybridRetrievalService(
        keyword_index=SqlKeywordIndex(uow.keyword_index),
        id_generator=IdGenerator(),
        retrieval_query_validator=query_validator,
        vector_store=vector_store,
        reranker=DeterministicHybridReranker(),
    )
    retrieval_workflow = RetrievalWorkflow(
        retrieval_service=retrieval_service,
        query_validator=query_validator,
        context_expander=RetrievalContextExpander(
            document_lookup_service=document_lookup_service,
        ),
        post_retrieval_guardrails=[
            DocumentRelevanceGuardrail(),
            RetrievalEvidenceGuardrail(),
        ],
    )
    exploration_service = DocumentExplorationService(document_lookup_service)

    # Resolve the answer generation model once so we can report it to the user.
    # answer_generation_llm falls back to general_llm when not explicitly set.
    generation_model: str | None = None
    answer_generation_service = None
    if enable_generation:
        generation_model = llm_settings.answer_generation_llm or llm_settings.general_llm
        llm_service = LLMService(
            OllamaLLMProvider(
                base_url=llm_settings.ollama_base_url,
                default_model=generation_model,
            )
        )
        answer_generation_service = AnswerGenerationService(
            llm_service=llm_service,
            answer_generation_model=generation_model,
        )

    workflow = QuestionAnsweringWorkflow(
        retrieval_workflow=retrieval_workflow,
        exploration_service=exploration_service,
        router=QuestionAnsweringRouter(),
        context_guardrails=[
            ContextFilteringGuardrail(),
            ContextQualityGuardrail(),
            ContextBudgetGuardrail(),
        ],
        answer_generation_service=answer_generation_service,
        post_answer_guardrails=(
            [
                SafetyAnswerGuardrail(),
                CitationGuardrail(),
                UnsupportedClaimGuardrail(),
                UnsupportedSuggestionGuardrail(),
                AnswerSupportGuardrail(),
            ]
            if enable_generation
            else []
        ),
    )
    return QARuntime(
        workflow=workflow,
        session=session,
        qdrant_client=qdrant_client,
        generation_model=generation_model,
    )


def _print_context_chunks(result) -> None:
    """Print each retrieved chunk with full metadata and up to 1000 chars of content."""
    if result.retrieval_result is None:
        print("  No retrieval result available.")
        return
    chunks = result.retrieval_result.final_chunks
    if not chunks:
        print("  No chunks retrieved.")
        return

    approved_set = set(result.approved_chunk_ids)
    sep = "-" * 72

    print()
    for i, chunk in enumerate(chunks, 1):
        status = "APPROVED" if chunk.chunk_id in approved_set else "REJECTED"
        page_info = _page_range(chunk.source)
        page_str = f" | {page_info}" if page_info else ""
        chunk_type = str(chunk.chunk_type).split(".")[-1].lower()
        score_str = f"{chunk.score:.4f}" if chunk.score is not None else "n/a"

        print(sep)
        print(
            f"  [{status}] #{i}"
            f" | score: {score_str}"
            f" | type: {chunk_type}"
            f"{page_str}"
        )
        print(
            f"  chunk: {_trunc(chunk.chunk_id, 44)}"
            f"  doc: {_trunc(chunk.document_id, 30)}"
        )
        if chunk.section_path:
            path_str = " > ".join(chunk.section_path)
            print(f"  path:  {_trunc(path_str, 80)}")

        content = chunk.content or ""
        preview = content[:1000].rstrip()
        if len(content) > 1000:
            preview += "\n  [… truncated]"
        print()
        for line in preview.splitlines():
            safe = line.encode("ascii", errors="replace").decode("ascii")
            print(f"    {safe}")
        print()

    print(sep)

    # Rejected IDs that didn't appear in final_chunks at all (shouldn't happen, guard only).
    in_chunks = {c.chunk_id for c in chunks}
    orphan = [rid for rid in result.rejected_chunk_ids if rid not in in_chunks]
    if orphan:
        print(f"\n  Rejected (not in retrieved set): {', '.join(_trunc(r, 20) for r in orphan)}")


def _generation_status_line(
    *,
    enable_generation: bool,
    service_configured: bool,
    model_name: str | None,
) -> str:
    if not enable_generation:
        return "disabled  (use --generate to enable)"
    if not service_configured:
        # This should not happen if ask_document.py is wired correctly.
        return "enabled but service NOT CONFIGURED  ← bug, report this"
    return f"enabled | model: {model_name or '(default)'}"


def _print_retrieval_result(
    result,
    *,
    show_context: bool,
    enable_generation: bool,
    service_configured: bool,
    model_name: str | None,
) -> None:
    n_approved = len(result.approved_chunk_ids)
    n_rejected = len(result.rejected_chunk_ids)
    confidence = result.confidence or "n/a"

    enough_ev = result.diagnostics.get("enough_evidence")
    evidence_str = ""
    if enough_ev is not None:
        evidence_str = f" | evidence: {'sufficient' if enough_ev else 'insufficient'}"

    print(f"Route: retrieval_qa | confidence: {confidence}{evidence_str}")

    gen_line = _generation_status_line(
        enable_generation=enable_generation,
        service_configured=service_configured,
        model_name=model_name,
    )
    print(f"Generation: {gen_line}")

    # Show the model actually used when the workflow reported it.
    diag_model = result.diagnostics.get("model_name")
    if diag_model and enable_generation and service_configured:
        print(f"Model used: {diag_model}")

    print()

    if result.answer_text:
        print("Answer")
        print("------")
        print(result.answer_text)

    if result.citations:
        print("\nCitations")
        print("---------")
        for i, cite in enumerate(result.citations, 1):
            print(f"  [{i}] {cite.display_text()}")

    print(f"\nContext: {n_approved} approved, {n_rejected} rejected")

    if show_context:
        _print_context_chunks(result)


def _print_exploration_result(result) -> None:
    print("Route: document_exploration\n")
    exp = result.document_exploration_result
    if exp is None:
        msg = result.safe_user_message or "No exploration result."
        print(msg)
        return

    ov = exp.overview
    title = ov.title or ov.file_name
    print(f"Document: {title}")
    print(
        f"  File: {ov.file_name} | Type: {ov.document_type}"
        f" | Pages: {ov.page_count or '-'}"
    )
    print(
        f"  Sections: {ov.section_count} | Chunks: {ov.chunk_count}"
        f" | Tables: {ov.table_count} | Identifiers: {ov.identifier_count}"
    )

    if exp.sections:
        max_sections = 20
        print(f"\nSections ({ov.section_count}):")
        for sec in exp.sections[:max_sections]:
            indent = "  " * (sec.level - 1)
            print(f"  {indent}{sec.title}")
        if len(exp.sections) > max_sections:
            print(f"  ... ({len(exp.sections) - max_sections} more)")

    if exp.identifiers:
        print(f"\nIdentifiers ({len(exp.identifiers)}):")
        for ident in exp.identifiers[:10]:
            print(f"  {ident.identifier_type}: {ident.raw_value}")
        if len(exp.identifiers) > 10:
            print(f"  ... ({len(exp.identifiers) - 10} more)")


def _print_blocked_result(result) -> None:
    route = str(result.route).split(".")[-1].lower()
    print(f"Route: {route}")
    if result.guardrail_decision:
        decision = str(result.guardrail_decision).split(".")[-1]
        print(f"Decision: {decision}")
    if result.safe_user_message:
        print(f"Message: {result.safe_user_message}")


def print_result(
    result,
    *,
    show_context: bool,
    document_id: str | None,
    document_name: str | None,
    enable_generation: bool,
    service_configured: bool,
    model_name: str | None,
) -> None:
    from src.application.workflows.question_answering import (  # noqa: WPS433
        QuestionAnsweringRoute,
    )

    if document_id:
        id_short = document_id[:16]
        print(f"Document: {document_name or document_id}  [{id_short}...]\n")

    route = result.route
    if route == QuestionAnsweringRoute.RETRIEVAL_QA:
        _print_retrieval_result(
            result,
            show_context=show_context,
            enable_generation=enable_generation,
            service_configured=service_configured,
            model_name=model_name,
        )
    elif route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION:
        _print_exploration_result(result)
    else:
        _print_blocked_result(result)


def print_result_json(
    result,
    *,
    question: str,
    show_context: bool,
    document_id: str | None,
    document_name: str | None,
    enable_generation: bool,
    service_configured: bool,
    model_name: str | None,
) -> None:
    from src.application.workflows.question_answering import (  # noqa: WPS433
        QuestionAnsweringRoute,
    )

    route = str(result.route).split(".")[-1] if result.route else None
    output: dict[str, Any] = {
        "route": route,
        "question": question,
        "document_id": document_id,
        "document_title": document_name,
        "answer_text": result.answer_text,
        "safe_user_message": result.safe_user_message,
        "guardrail_decision": (
            str(result.guardrail_decision).split(".")[-1]
            if result.guardrail_decision
            else None
        ),
        "confidence": result.confidence,
        "generation_enabled": enable_generation,
        "generation_configured": service_configured,
        "generation_model": model_name,
        "approved_chunk_ids": result.approved_chunk_ids,
        "rejected_chunk_ids": result.rejected_chunk_ids,
        "citations": [
            {
                "chunk_id": c.chunk_id,
                "document_name": c.document_name,
                "section_title": c.section_title,
                "page": getattr(c.source, "page_start", None),
            }
            for c in (result.citations or [])
        ],
    }

    if result.route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION:
        exp = result.document_exploration_result
        if exp is not None:
            ov = exp.overview
            output["overview"] = {
                "title": ov.title,
                "file_name": ov.file_name,
                "document_type": ov.document_type,
                "page_count": ov.page_count,
                "section_count": ov.section_count,
                "chunk_count": ov.chunk_count,
                "table_count": ov.table_count,
                "identifier_count": ov.identifier_count,
            }
            output["sections"] = [
                {
                    "title": s.title,
                    "level": s.level,
                    "parent_section_id": s.parent_section_id,
                }
                for s in exp.sections
            ]

    if show_context and result.retrieval_result is not None:
        approved_set = set(result.approved_chunk_ids)
        output["context_chunks"] = [
            {
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "score": c.score,
                "chunk_type": str(c.chunk_type).split(".")[-1].lower(),
                "section_path": c.section_path,
                "page_start": getattr(c.source, "page_start", None),
                "page_end": getattr(c.source, "page_end", None),
                "approved": c.chunk_id in approved_set,
                "content": c.content,
            }
            for c in result.retrieval_result.final_chunks
        ]

    print(json.dumps(output, indent=2))


def _write_retrieval_trace(
    *,
    runtime: QARuntime,
    question: str,
    document_id: str | None,
    top_k: int | None,
) -> None:
    try:
        import datetime  # noqa: WPS433

        from src.application.workflows.retrieval.tracing import (  # noqa: WPS433
            RetrievalTraceRecorder,
            RetrievalTraceWriter,
        )
        from src.domain.common import new_id  # noqa: WPS433
        from src.domain.retrieval import RetrievalQuery  # noqa: WPS433

        retrieval_wf = runtime.workflow._retrieval_workflow
        recorder = RetrievalTraceRecorder()
        query = RetrievalQuery(
            query_id=new_id("q"),
            query_text=question,
            top_k=top_k or 5,
            document_id=document_id,
        )
        retrieval_wf.run(query, trace_recorder=recorder)
        ts = datetime.datetime.utcnow().isoformat()
        trace = recorder.build(query_id=query.query_id, timestamp_iso=ts)
        writer = RetrievalTraceWriter()
        path = writer.write(trace)
        print_status(f"Trace written → {path}")
    except Exception as exc:
        print_status(f"Trace write failed: {exc}")


def close_runtime(runtime: QARuntime | None) -> None:
    if runtime is None:
        return
    session = getattr(runtime, "session", None)
    if session is not None:
        session.close()
    qdrant_client = getattr(runtime, "qdrant_client", None)
    _close_quietly(qdrant_client)


def _close_quietly(resource: Any) -> None:
    if resource is None:
        return
    close = getattr(resource, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            return


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    question = resolve_question(args)
    if not question:
        print(
            "Provide a question: python scripts/ask_document.py 'Your question here' --latest",
            file=sys.stderr,
        )
        return 1

    session = None
    runtime: QARuntime | None = None

    try:
        from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
        from src.config.settings import ingestion_settings  # noqa: WPS433
        from src.infrastructure.db.base import Base  # noqa: WPS433
        from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
            __all__ as _orm_models_loaded,
        )
        from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433

        bootstrap_application()
        Base.metadata.create_all(engine)
        session = SessionLocal()

        document_id, document_name = resolve_document(session, args)

        if document_id is None and (args.document_id or args.document or args.latest):
            print(
                "\nRun 'python scripts/list_documents.py' to see available documents.",
                file=sys.stderr,
            )
            return 1

        if document_id is None and not (args.document_id or args.document or args.latest):
            print(
                "Specify a document: --document-id ID | --document NAME | --latest",
                file=sys.stderr,
            )
            print(
                "Run 'python scripts/list_documents.py' to see available documents.",
                file=sys.stderr,
            )
            return 1

        # Honour both the CLI flag and the env-var default so that the workflow
        # never requests generation without a wired AnswerGenerationService.
        effective_generation = args.generate or ingestion_settings.enable_answer_generation

        if not args.json:
            disp = document_name or document_id
            print_status(f"Document: {disp}")
            if effective_generation:
                gen_src = "--generate" if args.generate else "ENABLE_ANSWER_GENERATION=true"
                print_status(f"Generation: enabled ({gen_src})")
            else:
                print_status("Generation: disabled  (pass --generate to enable LLM)")
            print_status("Building QA runtime...")

        runtime = build_qa_runtime(session, enable_generation=effective_generation)

        if not args.json and effective_generation:
            model_str = runtime.generation_model or "(unknown)"
            print_status(f"Answer generation model: {model_str}")

        if not args.json:
            print_status("Running question answering workflow...")

        from src.application.workflows.question_answering import (  # noqa: WPS433
            QuestionAnsweringRequest,
        )

        request = QuestionAnsweringRequest(
            question=question,
            document_id=document_id,
            top_k=args.top_k,
            include_context=args.show_context,
            allow_answer_generation=effective_generation,
        )
        result = runtime.workflow.run(request)

        if getattr(args, "trace", False):
            _write_retrieval_trace(
                runtime=runtime,
                question=question,
                document_id=document_id,
                top_k=args.top_k,
            )

        service_configured = runtime.generation_model is not None

        if args.json:
            print_result_json(
                result,
                question=question,
                show_context=args.show_context,
                document_id=document_id,
                document_name=document_name,
                enable_generation=effective_generation,
                service_configured=service_configured,
                model_name=runtime.generation_model,
            )
        else:
            print()
            print_result(
                result,
                show_context=args.show_context,
                document_id=document_id,
                document_name=document_name,
                enable_generation=effective_generation,
                service_configured=service_configured,
                model_name=runtime.generation_model,
            )

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        close_runtime(runtime)
        if runtime is None and session is not None:
            session.close()


if __name__ == "__main__":
    raise SystemExit(main())
