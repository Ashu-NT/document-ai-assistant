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
        "--retrieval-strategy",
        choices=(
            "auto",
            "hybrid",
            "identifier",
            "table",
            "section",
            "figure",
            "maintenance",
            "procedure",
            "specification",
            "troubleshooting",
            "certification",
            "drawing",
        ),
        default=None,
        help="Override V7 retrieval strategy selection or use auto selection.",
    )
    llm_retrieval_strategy_group = parser.add_mutually_exclusive_group()
    llm_retrieval_strategy_group.add_argument(
        "--llm-retrieval-strategy",
        dest="llm_retrieval_strategy",
        action="store_true",
        help="Enable validated LLM retrieval-strategy selection.",
    )
    llm_retrieval_strategy_group.add_argument(
        "--no-llm-retrieval-strategy",
        dest="llm_retrieval_strategy",
        action="store_false",
        help="Disable validated LLM retrieval-strategy selection.",
    )
    parser.set_defaults(llm_retrieval_strategy=None)
    parser.add_argument(
        "--show-retrieval-strategy",
        action="store_true",
        help="Print the selected retrieval strategy, reasoning, and plan.",
    )
    parser.add_argument(
        "--show-plan",
        action="store_true",
        help="Display the deterministic multi-step execution plan when one is used.",
    )
    deep_research_group = parser.add_mutually_exclusive_group()
    deep_research_group.add_argument(
        "--deep-research",
        dest="deep_research",
        action="store_true",
        help="Enable LangGraph V8 deep research routing and execution.",
    )
    deep_research_group.add_argument(
        "--no-deep-research",
        dest="deep_research",
        action="store_false",
        help="Disable LangGraph V8 deep research routing for this run.",
    )
    parser.set_defaults(deep_research=None)
    llm_research_planning_group = parser.add_mutually_exclusive_group()
    llm_research_planning_group.add_argument(
        "--llm-research-planning",
        dest="llm_research_planning",
        action="store_true",
        help="Enable validated LLM research planning for deep research requests.",
    )
    llm_research_planning_group.add_argument(
        "--no-llm-research-planning",
        dest="llm_research_planning",
        action="store_false",
        help="Disable validated LLM research planning for deep research requests.",
    )
    parser.set_defaults(llm_research_planning=None)
    parser.add_argument(
        "--show-research-plan",
        action="store_true",
        help="Print the deep research task plan when a V8 research route is used.",
    )
    parser.add_argument(
        "--show-research-trace",
        action="store_true",
        help="Print the deep research execution trace when a V8 research route is used.",
    )
    llm_planning_group = parser.add_mutually_exclusive_group()
    llm_planning_group.add_argument(
        "--llm-planning",
        dest="llm_planning",
        action="store_true",
        help="Enable validated LLM fallback planning for planned-task requests.",
    )
    llm_planning_group.add_argument(
        "--no-llm-planning",
        dest="llm_planning",
        action="store_false",
        help="Disable validated LLM fallback planning even if enabled in settings.",
    )
    parser.set_defaults(llm_planning=None)
    reflection_group = parser.add_mutually_exclusive_group()
    reflection_group.add_argument(
        "--reflection",
        dest="reflection",
        action="store_true",
        help="Enable LangGraph V6 reflection review for generated answers.",
    )
    reflection_group.add_argument(
        "--no-reflection",
        dest="reflection",
        action="store_false",
        help="Disable LangGraph V6 reflection review.",
    )
    parser.set_defaults(reflection=None)
    parser.add_argument(
        "--show-raw-plan",
        action="store_true",
        help="Display the raw LLM planning output when tracing is enabled.",
    )
    parser.add_argument(
        "--show-reflection",
        action="store_true",
        help="Print reflection reviewer decisions and scores when available.",
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print CLI execution metadata and debug-oriented status details.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str, *, enabled: bool = True) -> None:
    if enabled:
        print(f"[agent-cli] {message}", flush=True)


def _create_qdrant_client(qdrant_client_class):
    from src.config.settings import qdrant_settings

    if qdrant_settings.mode.lower() == "local":
        return qdrant_client_class(path=str(qdrant_settings.storage_path))
    return qdrant_client_class(host=qdrant_settings.host, port=qdrant_settings.port)


def build_agent_runtime(
    session,
    *,
    enable_generation: bool,
    enable_llm_planning: bool,
    enable_llm_research_planning: bool,
) -> AgentRuntime:
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
        LLMResearchPlanner,
        NodeFactory,
        ReflectionService,
        ReflectionValidator,
        ReflectionPromptBuilder,
        ReflectionJsonParser,
        ReflectionPolicy,
        EvidenceMerger,
        ResearchPolicy,
        RetryQueryBuilder,
        ClarificationBuilder,
        RetrievalRetryPolicy,
        SessionStateStore,
        ToolRegistry,
    )
    from src.application.langgraph.retrieval_strategy import (
        LLMStrategySelector,
        RetrievalPlanExecutor,
        RetrievalStrategyPolicy,
        RetrievalStrategyService,
        StrategyRetryPolicy,
    )
    from src.application.langgraph.planning import (
        LLMPlanProposer,
        PlanParser,
        PlanPolicy,
        PlanRepair,
        PlanValidator,
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
    from src.application.tools.retrieval import (
        RetrieveChunksTool,
        RetrieveFiguresTool,
        RetrieveIdentifiersTool,
        RetrieveTablesTool,
    )
    from src.application.validation.retrieval import RetrievalQueryValidator
    from src.application.workflows.question_answering import (
        QuestionAnsweringRouter,
        QuestionAnsweringWorkflow,
    )
    from src.application.workflows.retrieval import (
        RetrievalContextExpander,
        RetrievalWorkflow,
    )
    from src.config.settings import (
        embedding_settings,
        langgraph_settings,
        llm_settings,
        qdrant_settings,
    )
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
    planning_llm_service = None
    reflection_model = llm_settings.answer_generation_llm or llm_settings.general_llm
    reflection_llm_service = LLMService(
        OllamaLLMProvider(
            base_url=llm_settings.ollama_base_url,
            default_model=reflection_model,
        )
    )
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
    if enable_llm_planning or enable_llm_research_planning:
        planning_model = llm_settings.planning_llm or llm_settings.general_llm
        planning_llm_service = LLMService(
            OllamaLLMProvider(
                base_url=llm_settings.ollama_base_url,
                default_model=planning_model,
            )
        )
    retrieval_strategy_model = llm_settings.general_llm
    retrieval_strategy_llm_service = LLMService(
        OllamaLLMProvider(
            base_url=llm_settings.ollama_base_url,
            default_model=retrieval_strategy_model,
        )
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
    retrieve_chunks_tool = RetrieveChunksTool(retrieval_workflow)
    retrieve_tables_tool = RetrieveTablesTool(
        retrieve_chunks_tool,
        exploration_service,
    )
    retrieve_identifiers_tool = RetrieveIdentifiersTool(
        document_lookup_service,
        exploration_service,
        retrieve_chunks_tool,
    )
    retrieve_figures_tool = RetrieveFiguresTool(
        retrieve_chunks_tool,
        exploration_service,
    )
    tool_registry = ToolRegistry(
        list_documents_tool=ListDocumentsTool(document_catalog_service),
        find_document_tool=find_document_tool,
        document_details_tool=DocumentDetailsTool(document_catalog_service),
        explore_document_tool=ExploreDocumentTool(exploration_service),
        retrieve_chunks_tool=retrieve_chunks_tool,
        retrieve_tables_tool=retrieve_tables_tool,
        retrieve_identifiers_tool=retrieve_identifiers_tool,
        retrieve_figures_tool=retrieve_figures_tool,
        answer_question_tool=AnswerQuestionTool(
            qa_workflow,
            find_document_tool=find_document_tool,
        ),
        run_quality_gate_tool=RunQualityGateTool(),
        retrieval_trace_tool=RetrievalTraceTool(retrieval_workflow),
    )
    retrieval_strategy_policy = RetrievalStrategyPolicy(
        enabled=langgraph_settings.retrieval_strategy_enabled,
        llm_strategy_enabled=langgraph_settings.llm_retrieval_strategy_enabled,
    )
    node_factory = NodeFactory(
        llm_plan_proposer=(
            LLMPlanProposer(
                planning_llm_service,
                model=llm_settings.planning_llm or llm_settings.general_llm,
            )
            if planning_llm_service is not None
            else None
        ),
        plan_parser=PlanParser(),
        plan_validator=PlanValidator(),
        plan_policy=PlanPolicy(max_steps=langgraph_settings.max_steps),
        plan_repair=PlanRepair(),
        reflection_service=ReflectionService(
            llm_service=reflection_llm_service,
            prompt_builder=ReflectionPromptBuilder(),
            json_parser=ReflectionJsonParser(),
            validator=ReflectionValidator(),
            policy=ReflectionPolicy(enabled=True),
            model=reflection_model,
        ),
        evidence_merger=EvidenceMerger(),
        retry_query_builder=RetryQueryBuilder(),
        clarification_builder=ClarificationBuilder(),
        retrieval_retry_policy=RetrievalRetryPolicy(),
        retrieval_strategy_service=RetrievalStrategyService(
            llm_selector=LLMStrategySelector(
                retrieval_strategy_llm_service,
                model=retrieval_strategy_model,
            ),
            policy=retrieval_strategy_policy,
        ),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=retrieval_strategy_policy,
        strategy_retry_policy=StrategyRetryPolicy(),
        llm_research_planner=(
            LLMResearchPlanner(
                planning_llm_service,
                model=llm_settings.planning_llm or llm_settings.general_llm,
            )
            if planning_llm_service is not None and enable_llm_research_planning
            else None
        ),
        research_policy=ResearchPolicy(
            enabled=langgraph_settings.deep_research_enabled,
            llm_research_planning_enabled=(
                langgraph_settings.llm_research_planning_enabled
            ),
        ),
    )
    graph = GraphFactory(node_factory=node_factory).create_document_agent_graph(
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


def _console_safe_text(value: str | None) -> str:
    if value is None:
        return ""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return value.encode(encoding, errors="replace").decode(encoding, errors="replace")
    except LookupError:
        return value.encode("utf-8", errors="replace").decode("utf-8", errors="replace")


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
        print(_console_safe_text(f"[{index}] {_chunk_label(chunk)} | {chunk_type}"))
        print(_console_safe_text(f"  document: {document_title} ({document_id})"))
        print(_console_safe_text(f"  section:  {section_path_text}"))
        print(f"  pages:    {_page_range_label(chunk)}")
        print(f"  score:    {score_text}")
        print(_console_safe_text(f"  content:  {_preview_text(chunk.get('content'))}"))
        print()


def print_retrieval_strategy(result) -> None:
    data = result.data or {}
    decision = data.get("retrieval_strategy_decision")
    plan = data.get("retrieval_plan")
    print("\nRetrieval Strategy")
    print("------------------")
    if not isinstance(decision, dict):
        if _print_research_task_strategies(data):
            return
        print("No retrieval strategy decision was recorded.")
        return
    print(f"Primary: {decision.get('primary_strategy') or '-'}")
    secondaries = decision.get("secondary_strategies") or []
    print(
        "Secondary: "
        + (", ".join(str(item) for item in secondaries) if secondaries else "-")
    )
    confidence = decision.get("confidence")
    if isinstance(confidence, int | float):
        print(f"Confidence: {float(confidence):.2f}")
    else:
        print("Confidence: -")
    print(f"Reason: {decision.get('reason') or '-'}")
    if isinstance(plan, dict):
        steps = plan.get("steps") or []
        if isinstance(steps, list) and steps:
            print("Plan:")
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    continue
                tool_name = step.get("tool_name") or "-"
                query = _preview_text(step.get("query"), limit=120)
                print(f"{index}. {tool_name} - {query}")
    errors = data.get("retrieval_strategy_errors") or []
    if errors:
        print(f"Errors: {', '.join(str(item) for item in errors)}")


def _print_research_task_strategies(data: dict[str, Any]) -> bool:
    research_plan = data.get("research_plan")
    if not isinstance(research_plan, dict):
        return False
    tasks = research_plan.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return False
    research_trace = data.get("research_trace") or {}
    strategy_by_task = {}
    if isinstance(research_trace, dict):
        raw = research_trace.get("retrieval_strategies_per_task")
        if isinstance(raw, dict):
            strategy_by_task = raw
    for task in tasks:
        if not isinstance(task, dict):
            continue
        title = str(task.get("title") or "Task").strip()
        task_id = str(task.get("task_id") or "")
        primary = (
            str(strategy_by_task.get(task_id) or "").strip()
            or str(task.get("strategy_hint") or "").strip()
            or "-"
        )
        secondaries = _task_secondary_strategy_hints(task)
        print(f"Task: {title}")
        print(f"Primary: {primary}")
        print(
            "Secondary: "
            + (", ".join(secondaries) if secondaries else "-")
        )
        print()
    return True


def _task_secondary_strategy_hints(task: dict[str, Any]) -> list[str]:
    diagnostics = task.get("diagnostics")
    if isinstance(diagnostics, dict):
        secondaries = diagnostics.get("secondary_strategies")
        if isinstance(secondaries, list):
            return [str(item) for item in secondaries if str(item).strip()]
    title = str(task.get("title") or "").casefold()
    if "maintenance" in title or "specification" in title or "technical" in title:
        return ["TABLE_LOOKUP"]
    return []


def print_reflection(result) -> None:
    data = result.data or {}
    reflection_result = data.get("reflection_result")
    if not isinstance(reflection_result, dict):
        print("\nReflection")
        print("----------")
        print("No reflection result available.")
        return
    decision = (reflection_result.get("decision") or {}).get("decision") or data.get(
        "reflection_decision"
    )
    reason = (reflection_result.get("decision") or {}).get("reason")
    retry_query = (reflection_result.get("decision") or {}).get("retry_query")
    print("\nReflection")
    print("----------")
    print(f"Decision: {decision or '-'}")
    print(f"Overall score: {data.get('reflection_score') if data.get('reflection_score') is not None else '-'}")
    print(
        f"Answer score: {(reflection_result.get('answer_quality_score') if reflection_result.get('answer_quality_score') is not None else '-')}"
    )
    print(
        f"Evidence score: {(reflection_result.get('evidence_quality_score') if reflection_result.get('evidence_quality_score') is not None else '-')}"
    )
    if reason:
        print(f"Reason: {reason}")
    if retry_query:
        print(f"Retry query: {retry_query}")
    merged_chunk_ids = data.get("merged_chunk_ids") or []
    if merged_chunk_ids:
        print(f"Merged chunks: {len(merged_chunk_ids)}")


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


def print_raw_plan(raw_llm_plan: str | None) -> None:
    print("\nRaw Plan")
    print("--------")
    if not raw_llm_plan:
        print("No raw LLM plan was captured.")
        return
    print(raw_llm_plan)


def print_research_plan(research_plan: dict[str, Any] | None) -> None:
    print("\nResearch Plan")
    print("-------------")
    if not isinstance(research_plan, dict):
        print("No deep research plan was recorded.")
        return
    tasks = research_plan.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        print("No research tasks were recorded.")
        return
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            continue
        title = task.get("title") or f"Task {index}"
        strategy_hint = task.get("strategy_hint") or "-"
        print(f"{index}. {title} ({strategy_hint})")


def print_research_trace(research_trace: dict[str, Any] | None) -> None:
    print("\nResearch Trace")
    print("--------------")
    if not isinstance(research_trace, dict):
        print("No deep research trace was recorded.")
        return
    print(f"Plan source: {research_trace.get('plan_source') or '-'}")
    evidence_counts = research_trace.get("evidence_counts_per_task") or {}
    if isinstance(evidence_counts, dict) and evidence_counts:
        print("Evidence counts:")
        for task_id, count in evidence_counts.items():
            print(f"- {task_id}: {count}")
    gaps = research_trace.get("gaps") or []
    if isinstance(gaps, list):
        print(f"Gaps: {len(gaps)}")


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
        "reflection_result": data.get("reflection_result"),
        "reflection_decision": data.get("reflection_decision"),
        "reflection_score": data.get("reflection_score"),
        "retry_query": data.get("retry_query"),
        "selected_document_id": data.get("selected_document_id"),
        "selected_document_title": data.get("selected_document_title"),
        "retrieval_strategy_decision": data.get("retrieval_strategy_decision"),
        "retrieval_plan": data.get("retrieval_plan"),
        "retrieval_execution_result": data.get("retrieval_execution_result"),
        "retrieval_strategy_trace": data.get("retrieval_strategy_trace"),
        "selected_retrieval_strategies": data.get("selected_retrieval_strategies", []),
        "retrieval_strategy_errors": data.get("retrieval_strategy_errors", []),
        "pending_clarification": data.get("pending_clarification"),
        "clarification_options": data.get("clarification_options", []),
        "should_exit": data.get("should_exit", False),
        "context_chunks": data.get("context_chunks", []),
        "citations": data.get("citations", []),
        "execution_plan": data.get("execution_plan"),
        "validated_plan": data.get("validated_plan"),
        "plan_steps": data.get("plan_steps", []),
        "plan_results": data.get("plan_results", {}),
        "plan_success": data.get("plan_success"),
        "failed_plan_step": data.get("failed_plan_step"),
        "planning_source": data.get("planning_source"),
        "planning_errors": data.get("planning_errors", []),
        "planning_warnings": data.get("planning_warnings", []),
        "research_goal": data.get("research_goal"),
        "research_plan": data.get("research_plan"),
        "research_task_results": data.get("research_task_results", []),
        "research_gaps": data.get("research_gaps", []),
        "research_report": data.get("research_report"),
        "research_trace": data.get("research_trace"),
        "diagnostics": result.diagnostics or {},
    }
    if include_trace:
        payload["trace"] = result.trace or []
        if data.get("raw_llm_plan"):
            payload["raw_llm_plan"] = data.get("raw_llm_plan")
        if data.get("raw_llm_research_plan"):
            payload["raw_llm_research_plan"] = data.get("raw_llm_research_plan")
    return payload


def print_graph_result(
    result,
    *,
    show_debug: bool = False,
    show_plan: bool = False,
    show_raw_plan: bool = False,
    show_research_plan: bool = False,
    show_research_trace: bool = False,
    show_context: bool,
    show_trace: bool,
    show_reflection: bool = False,
    show_retrieval_strategy: bool = False,
) -> None:
    if show_debug:
        print(f"Route: {result.route or '-'}")
        print(f"Success: {result.success}")
    answer_text = (result.data or {}).get("answer") or result.response_text
    if answer_text:
        if show_debug:
            print()
        print(_console_safe_text(answer_text))
    answer_intent = (result.data or {}).get("answer_intent")
    if answer_intent and show_debug:
        print(f"\nAnswer intent: {answer_intent}")
    if show_plan:
        print_execution_plan(
            (result.data or {}).get("execution_plan"),
            (result.data or {}).get("plan_steps", []),
        )
    if show_retrieval_strategy:
        print_retrieval_strategy(result)
    if show_raw_plan:
        print_raw_plan((result.data or {}).get("raw_llm_plan"))
    if show_research_plan:
        print_research_plan((result.data or {}).get("research_plan"))
    if show_research_trace:
        print_research_trace((result.data or {}).get("research_trace"))
    if show_context:
        print_context_chunks((result.data or {}).get("context_chunks", []))
    if show_reflection:
        print_reflection(result)
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
    llm_planning_enabled: bool,
    deep_research_enabled: bool = False,
    llm_research_planning_enabled: bool = False,
    show_research_plan: bool = False,
    show_research_trace: bool = False,
    reflection_enabled: bool = False,
    show_reflection: bool = False,
    retrieval_strategy_enabled: bool = False,
    llm_retrieval_strategy_enabled: bool = False,
    show_retrieval_strategy: bool = False,
    requested_retrieval_strategy: str | None = None,
    show_plan: bool = False,
    show_raw_plan: bool = False,
    top_k: int | None = None,
):
    return runtime.graph.run(
        user_input,
        document_id=document_id,
        document_query=document_query,
        session_id=session_id,
        allow_answer_generation=allow_answer_generation,
        include_context=include_context,
        llm_planning_enabled=llm_planning_enabled,
        deep_research_enabled=deep_research_enabled,
        llm_research_planning_enabled=llm_research_planning_enabled,
        show_research_plan=show_research_plan,
        show_research_trace=show_research_trace,
        reflection_enabled=reflection_enabled,
        show_reflection=show_reflection,
        retrieval_strategy_enabled=retrieval_strategy_enabled,
        llm_retrieval_strategy_enabled=llm_retrieval_strategy_enabled,
        show_retrieval_strategy=show_retrieval_strategy,
        requested_retrieval_strategy=requested_retrieval_strategy,
        show_plan=show_plan,
        show_raw_plan=show_raw_plan,
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
    llm_planning_enabled: bool,
    deep_research_enabled: bool = False,
    llm_research_planning_enabled: bool = False,
    show_research_plan: bool = False,
    show_research_trace: bool = False,
    reflection_enabled: bool = False,
    show_reflection: bool = False,
    retrieval_strategy_enabled: bool = False,
    llm_retrieval_strategy_enabled: bool = False,
    show_retrieval_strategy: bool = False,
    requested_retrieval_strategy: str | None = None,
    show_plan: bool = False,
    show_raw_plan: bool = False,
    top_k: int | None = None,
    emit_json: bool = False,
    show_trace: bool = False,
    show_debug: bool = False,
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
            llm_planning_enabled=llm_planning_enabled,
            deep_research_enabled=deep_research_enabled,
            llm_research_planning_enabled=llm_research_planning_enabled,
            show_research_plan=show_research_plan,
            show_research_trace=show_research_trace,
            reflection_enabled=reflection_enabled,
            show_reflection=show_reflection,
            retrieval_strategy_enabled=retrieval_strategy_enabled,
            llm_retrieval_strategy_enabled=llm_retrieval_strategy_enabled,
            show_retrieval_strategy=show_retrieval_strategy,
            requested_retrieval_strategy=requested_retrieval_strategy,
            show_plan=show_plan,
            show_raw_plan=show_raw_plan,
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
                show_debug=show_debug,
                show_plan=show_plan,
                show_raw_plan=show_raw_plan and show_trace,
                show_research_plan=show_research_plan,
                show_research_trace=show_research_trace,
                show_context=include_context,
                show_trace=show_trace,
                show_reflection=show_reflection,
                show_retrieval_strategy=show_retrieval_strategy,
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
        from src.config.settings import ingestion_settings, langgraph_settings
        from src.infrastructure.db.base import Base
        from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded
        from src.infrastructure.db.session import SessionLocal, engine

        bootstrap_application()
        Base.metadata.create_all(engine)
        session = SessionLocal()

        effective_generation = args.generate or ingestion_settings.enable_answer_generation
        effective_llm_planning = (
            args.llm_planning
            if args.llm_planning is not None
            else langgraph_settings.llm_planning_enabled
        )
        effective_reflection = (
            args.reflection
            if args.reflection is not None
            else langgraph_settings.reflection_enabled
        )
        effective_llm_retrieval_strategy = (
            args.llm_retrieval_strategy
            if args.llm_retrieval_strategy is not None
            else langgraph_settings.llm_retrieval_strategy_enabled
        )
        effective_deep_research = (
            args.deep_research
            if args.deep_research is not None
            else langgraph_settings.deep_research_enabled
        )
        effective_llm_research_planning = (
            args.llm_research_planning
            if args.llm_research_planning is not None
            else langgraph_settings.llm_research_planning_enabled
        )
        effective_retrieval_strategy = (
            langgraph_settings.retrieval_strategy_enabled
            or args.retrieval_strategy is not None
            or effective_llm_retrieval_strategy
            or args.show_retrieval_strategy
        )
        effective_session_id = build_session_id(args.session_id) if args.interactive else args.session_id
        if args.show_raw_plan and not args.trace:
            print("--show-raw-plan requires --trace.", file=sys.stderr)
            return 1
        print_status("Building document agent runtime...", enabled=args.debug)
        runtime = build_agent_runtime(
            session,
            enable_generation=effective_generation,
            enable_llm_planning=effective_llm_planning,
            enable_llm_research_planning=effective_llm_research_planning,
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
                llm_planning_enabled=effective_llm_planning,
                deep_research_enabled=effective_deep_research,
                llm_research_planning_enabled=effective_llm_research_planning,
                show_research_plan=args.show_research_plan,
                show_research_trace=args.show_research_trace,
                reflection_enabled=effective_reflection,
                show_reflection=args.show_reflection,
                retrieval_strategy_enabled=effective_retrieval_strategy,
                llm_retrieval_strategy_enabled=effective_llm_retrieval_strategy,
                show_retrieval_strategy=args.show_retrieval_strategy,
                requested_retrieval_strategy=args.retrieval_strategy,
                show_plan=args.show_plan,
                show_raw_plan=args.show_raw_plan,
                top_k=args.top_k,
                emit_json=args.json,
                show_trace=args.trace,
                show_debug=args.debug,
            )

        print_status("Running document agent graph...", enabled=args.debug)
        result = run_graph_request(
            runtime,
            args.user_input,
            document_id=args.document_id,
            document_query=args.document,
            session_id=effective_session_id,
            allow_answer_generation=effective_generation,
            include_context=args.show_context,
            llm_planning_enabled=effective_llm_planning,
            deep_research_enabled=effective_deep_research,
            llm_research_planning_enabled=effective_llm_research_planning,
            show_research_plan=args.show_research_plan,
            show_research_trace=args.show_research_trace,
            reflection_enabled=effective_reflection,
            show_reflection=args.show_reflection,
            retrieval_strategy_enabled=effective_retrieval_strategy,
            llm_retrieval_strategy_enabled=effective_llm_retrieval_strategy,
            show_retrieval_strategy=args.show_retrieval_strategy,
            requested_retrieval_strategy=args.retrieval_strategy,
            show_plan=args.show_plan,
            show_raw_plan=args.show_raw_plan,
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
                show_debug=args.debug,
                show_plan=args.show_plan,
                show_raw_plan=args.show_raw_plan and args.trace,
                show_research_plan=args.show_research_plan,
                show_research_trace=args.show_research_trace,
                show_context=args.show_context,
                show_trace=args.trace,
                show_reflection=args.show_reflection,
                show_retrieval_strategy=args.show_retrieval_strategy,
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
