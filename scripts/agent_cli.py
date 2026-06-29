from __future__ import annotations

"""
Deterministic CLI entrypoint for the first LangGraph document agent.

Usage:
    python scripts/agent_cli.py "list documents"
    python scripts/agent_cli.py "find document pressure transmitter"
    python scripts/agent_cli.py "explore document pressure transmitter"
    python scripts/agent_cli.py "What is the oil change interval?" --document FWC12
    python scripts/agent_cli.py "retrieve shaft seal lubrication" --document FWC12 --show-context
    python scripts/agent_cli.py "run quality gate"
"""

import argparse
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)


@dataclass(slots=True)
class AgentRuntime:
    graph: Any
    session: Any = None
    qdrant_client: Any = None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the deterministic LangGraph document agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/agent_cli.py 'list documents'\n"
            "  python scripts/agent_cli.py 'find document pressure transmitter'\n"
            "  python scripts/agent_cli.py 'What is the oil change interval?' --document FWC12\n"
        ),
    )
    parser.add_argument(
        "user_input",
        nargs="?",
        help="The command or question to route through the document agent.",
    )
    parser.add_argument(
        "--session-id",
        metavar="ID",
        help="Optional session ID for stateful one-shot or interactive continuity.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run an interactive stateful CLI loop.",
    )
    parser.add_argument(
        "--document",
        "-d",
        metavar="NAME",
        help="Optional document alias or title hint.",
    )
    parser.add_argument(
        "--document-id",
        metavar="ID",
        help="Optional document ID.",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Enable answer generation via the configured LLM.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        metavar="N",
        help="Override retrieval top-k for retrieval and QA routes.",
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Include expanded retrieval context in downstream QA/retrieval tools.",
    )
    parser.add_argument(
        "--show-plan",
        action="store_true",
        help="Display the deterministic multi-step execution plan when one is used.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the graph result as JSON.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print the graph node trace after execution.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[agent-cli] {message}", flush=True)


def _create_qdrant_client(qdrant_client_class):
    from src.config.settings import qdrant_settings

    if qdrant_settings.mode.lower() == "local":
        return qdrant_client_class(path=str(qdrant_settings.storage_path))
    return qdrant_client_class(host=qdrant_settings.host, port=qdrant_settings.port)


def build_agent_runtime(session, *, enable_generation: bool) -> AgentRuntime:
    from qdrant_client import QdrantClient

    from src.application.guardrails.answering import (
        AnswerSupportGuardrail,
        CitationGuardrail,
        SafetyAnswerGuardrail,
        UnsupportedClaimGuardrail,
        UnsupportedSuggestionGuardrail,
    )
    from src.application.guardrails.context import (
        ContextBudgetGuardrail,
        ContextFilteringGuardrail,
        ContextQualityGuardrail,
        ScopedDocumentConsistencyGuardrail,
    )
    from src.application.guardrails.retrieval import (
        DocumentRelevanceGuardrail,
        RetrievalEvidenceGuardrail,
    )
    from src.application.langgraph import (
        ConversationMemory,
        GraphFactory,
        SessionStateStore,
        ToolRegistry,
    )
    from src.application.services.ai import LLMService
    from src.application.services.answer_generation import AnswerGenerationService
    from src.application.services.document import (
        DocumentCatalogService,
        DocumentLookupService,
    )
    from src.application.services.document_exploration import (
        DocumentExplorationService,
    )
    from src.application.services.retrieval import HybridRetrievalService
    from src.application.tools.documents import (
        DocumentDetailsTool,
        FindDocumentTool,
        ListDocumentsTool,
    )
    from src.application.tools.evaluation import (
        RetrievalTraceTool,
        RunQualityGateTool,
    )
    from src.application.tools.exploration import ExploreDocumentTool
    from src.application.tools.question_answering import AnswerQuestionTool
    from src.application.tools.retrieval import RetrieveChunksTool
    from src.application.validation.retrieval import RetrievalQueryValidator
    from src.application.workflows.question_answering import (
        QuestionAnsweringRouter,
        QuestionAnsweringWorkflow,
    )
    from src.application.workflows.retrieval import (
        RetrievalContextExpander,
        RetrievalWorkflow,
    )
    from src.config.settings import embedding_settings, llm_settings, qdrant_settings
    from src.infrastructure.ai.embeddings import create_embedding_provider
    from src.infrastructure.ai.llm import OllamaLLMProvider
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
    from src.infrastructure.retrieval.keyword import SqlKeywordIndex
    from src.infrastructure.retrieval.rerankers import (
        DeterministicHybridReranker,
    )
    from src.infrastructure.retrieval.vector import QdrantVectorStore
    from src.shared.ids import IdGenerator

    uow = SqlAlchemyUnitOfWork(session)
    query_validator = RetrievalQueryValidator()
    embedding_provider = create_embedding_provider()
    qdrant_client = _create_qdrant_client(QdrantClient)

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        mapping_repository=uow.vector_mappings,
        collection_name=qdrant_settings.collection,
        embedding_model=embedding_settings.model_name,
        query_embedding_provider=embedding_provider,
        document_repository=uow.documents,
    )
    document_catalog_service = DocumentCatalogService(uow.documents)
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

    qa_workflow = QuestionAnsweringWorkflow(
        retrieval_workflow=retrieval_workflow,
        exploration_service=exploration_service,
        router=QuestionAnsweringRouter(),
        context_guardrails=[
            ScopedDocumentConsistencyGuardrail(),
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

    find_document_tool = FindDocumentTool(document_catalog_service)
    tool_registry = ToolRegistry(
        list_documents_tool=ListDocumentsTool(document_catalog_service),
        find_document_tool=find_document_tool,
        document_details_tool=DocumentDetailsTool(document_catalog_service),
        explore_document_tool=ExploreDocumentTool(exploration_service),
        retrieve_chunks_tool=RetrieveChunksTool(retrieval_workflow),
        answer_question_tool=AnswerQuestionTool(
            qa_workflow,
            find_document_tool=find_document_tool,
        ),
        run_quality_gate_tool=RunQualityGateTool(),
        retrieval_trace_tool=RetrievalTraceTool(retrieval_workflow),
    )
    graph = GraphFactory().create_document_agent_graph(
        tool_registry=tool_registry,
        memory=ConversationMemory(
            max_messages=20,
            session_state_store=SessionStateStore(),
        ),
    )
    return AgentRuntime(
        graph=graph,
        session=session,
        qdrant_client=qdrant_client,
    )


def print_trace(trace_entries: list[dict[str, Any]]) -> None:
    print("\nTrace")
    print("-----")
    for entry in trace_entries:
        node_name = entry.get("node_name")
        elapsed_ms = entry.get("elapsed_ms")
        success = entry.get("success")
        tool_name = entry.get("tool_name") or "-"
        print(
            f"{node_name}: success={success} | elapsed_ms={elapsed_ms} | tool={tool_name}"
        )


def _short_id(value: str | None, limit: int = 12) -> str:
    if not value:
        return "-"
    if len(value) <= limit:
        return value
    return value[:limit]


def _preview_text(value: str | None, limit: int = 400) -> str:
    if not value:
        return "-"
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _page_range_label(chunk: dict[str, Any]) -> str:
    source = chunk.get("source") or {}
    if not isinstance(source, dict):
        return "-"
    page_start = source.get("page_start")
    page_end = source.get("page_end")
    if page_start is None:
        return "-"
    if page_end is not None and page_end != page_start:
        return f"{page_start}-{page_end}"
    return str(page_start)


def _chunk_label(chunk: dict[str, Any]) -> str:
    section_title = chunk.get("section_title")
    if section_title:
        return str(section_title)
    section_path = chunk.get("section_path") or []
    if isinstance(section_path, list) and section_path:
        return str(section_path[-1])
    chunk_id = chunk.get("chunk_id")
    return _short_id(str(chunk_id) if chunk_id else None, limit=16)


def print_context_chunks(
    context_chunks: list[dict[str, Any]],
) -> None:
    print("\nContext Chunks")
    print("--------------")
    if not context_chunks:
        print("No context chunks available.")
        return

    for index, chunk in enumerate(context_chunks, start=1):
        chunk_type = chunk.get("chunk_type") or "unknown"
        document_title = chunk.get("document_title") or "-"
        document_id = _short_id(chunk.get("document_id"))
        section_path = chunk.get("section_path") or []
        section_path_text = (
            " > ".join(str(part) for part in section_path)
            if isinstance(section_path, list) and section_path
            else "-"
        )
        score = chunk.get("score")
        score_text = f"{float(score):.4f}" if isinstance(score, int | float) else "-"
        print(f"[{index}] {_chunk_label(chunk)} | {chunk_type}")
        print(f"  document: {document_title} ({document_id})")
        print(f"  section:  {section_path_text}")
        print(f"  pages:    {_page_range_label(chunk)}")
        print(f"  score:    {score_text}")
        print(f"  content:  {_preview_text(chunk.get('content'))}")
        print()


def print_execution_plan(
    execution_plan: dict[str, Any] | None,
    plan_steps: list[dict[str, Any]],
) -> None:
    print("\nPlan")
    print("----")
    if not isinstance(execution_plan, dict) or not plan_steps:
        print("No multi-step plan was used.")
        return
    for index, step in enumerate(plan_steps, start=1):
        description = step.get("description") or step.get("tool_name") or f"Step {index}"
        print(f"{index}. {description}")


def build_json_output(
    result,
    *,
    include_trace: bool,
) -> dict[str, Any]:
    data = result.data or {}
    payload = {
        "route": result.route,
        "success": result.success,
        "answer": data.get("answer") or result.response_text,
        "answer_intent": data.get("answer_intent"),
        "document_id": data.get("document_id"),
        "selected_document_id": data.get("selected_document_id"),
        "selected_document_title": data.get("selected_document_title"),
        "pending_clarification": data.get("pending_clarification"),
        "clarification_options": data.get("clarification_options", []),
        "should_exit": data.get("should_exit", False),
        "context_chunks": data.get("context_chunks", []),
        "citations": data.get("citations", []),
        "execution_plan": data.get("execution_plan"),
        "plan_steps": data.get("plan_steps", []),
        "plan_results": data.get("plan_results", {}),
        "plan_success": data.get("plan_success"),
        "failed_plan_step": data.get("failed_plan_step"),
        "diagnostics": result.diagnostics or {},
    }
    if include_trace:
        payload["trace"] = result.trace or []
    return payload


def print_graph_result(
    result,
    *,
    show_plan: bool = False,
    show_context: bool,
    show_trace: bool,
) -> None:
    print(f"Route: {result.route or '-'}")
    print(f"Success: {result.success}")
    if result.response_text:
        print()
        print(result.response_text)
    answer_intent = (result.data or {}).get("answer_intent")
    if answer_intent:
        print(f"\nAnswer intent: {answer_intent}")
    if show_context:
        print_context_chunks((result.data or {}).get("context_chunks", []))
    if show_trace:
        print_trace(result.trace or [])


def build_session_id(session_id: str | None) -> str:
    if session_id:
        return session_id
    return f"cli-{uuid4().hex[:12]}"


def run_graph_request(
    runtime: AgentRuntime,
    user_input: str,
    *,
    document_id: str | None,
    document_query: str | None,
    session_id: str | None,
    allow_answer_generation: bool,
    include_context: bool,
    show_plan: bool = False,
    top_k: int | None,
):
    return runtime.graph.run(
        user_input,
        document_id=document_id,
        document_query=document_query,
        session_id=session_id,
        allow_answer_generation=allow_answer_generation,
        include_context=include_context,
        show_plan=show_plan,
        top_k=top_k,
    )


def run_interactive_loop(
    runtime: AgentRuntime,
    *,
    session_id: str,
    initial_user_input: str | None,
    document_id: str | None,
    document_query: str | None,
    allow_answer_generation: bool,
    include_context: bool,
    show_plan: bool = False,
    top_k: int | None,
    emit_json: bool,
    show_trace: bool,
) -> int:
    print_status(f"Interactive session started: {session_id}")

    pending_inputs: list[str] = []
    if initial_user_input:
        pending_inputs.append(initial_user_input)

    while True:
        if pending_inputs:
            user_input = pending_inputs.pop(0)
        else:
            try:
                user_input = input("document-agent> ").strip()
            except EOFError:
                print()
                return 0
            except KeyboardInterrupt:
                print("\nInterrupted.")
                return 1

        if not user_input:
            continue

        result = run_graph_request(
            runtime,
            user_input,
            document_id=document_id,
            document_query=document_query,
            session_id=session_id,
            allow_answer_generation=allow_answer_generation,
            include_context=include_context,
            show_plan=show_plan,
            top_k=top_k,
        )

        if emit_json:
            print(
                json.dumps(
                    build_json_output(result, include_trace=show_trace),
                    indent=2,
                )
            )
        else:
            print_graph_result(
                result,
                show_plan=show_plan,
                show_context=include_context,
                show_trace=show_trace,
            )

        if (result.data or {}).get("should_exit"):
            return 0 if result.success else 1


def close_runtime(runtime: AgentRuntime | None) -> None:
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
    if not args.interactive and not args.user_input:
        print("Provide a command or question.", file=sys.stderr)
        return 1

    session = None
    runtime: AgentRuntime | None = None

    try:
        from src.bootstrap.startup import bootstrap_application
        from src.config.settings import ingestion_settings
        from src.infrastructure.db.base import Base
        from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded
        from src.infrastructure.db.session import SessionLocal, engine

        bootstrap_application()
        Base.metadata.create_all(engine)
        session = SessionLocal()

        effective_generation = args.generate or ingestion_settings.enable_answer_generation
        effective_session_id = build_session_id(args.session_id) if args.interactive else args.session_id
        print_status("Building document agent runtime...")
        runtime = build_agent_runtime(
            session,
            enable_generation=effective_generation,
        )
        if args.interactive:
            return run_interactive_loop(
                runtime,
                session_id=effective_session_id or build_session_id(None),
                initial_user_input=args.user_input,
                document_id=args.document_id,
                document_query=args.document,
                allow_answer_generation=effective_generation,
                include_context=args.show_context,
                show_plan=args.show_plan,
                top_k=args.top_k,
                emit_json=args.json,
                show_trace=args.trace,
            )

        print_status("Running document agent graph...")
        result = run_graph_request(
            runtime,
            args.user_input,
            document_id=args.document_id,
            document_query=args.document,
            session_id=effective_session_id,
            allow_answer_generation=effective_generation,
            include_context=args.show_context,
            show_plan=args.show_plan,
            top_k=args.top_k,
        )

        if args.json:
            print(
                json.dumps(
                    build_json_output(
                        result,
                        include_trace=args.trace,
                    ),
                    indent=2,
                )
            )
        else:
            print_graph_result(
                result,
                show_plan=args.show_plan,
                show_context=args.show_context,
                show_trace=args.trace,
            )

        return 0 if result.success else 1

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
