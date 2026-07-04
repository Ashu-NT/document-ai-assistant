from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.common import GraphResult


class _LazyIngestionWorkflow:
    """Defers building the full `IngestionWorkflow` until ingest or reingest
    is actually invoked.

    `IngestDocumentTool`/`ReingestDocumentTool` are guardrail-blocked from
    ever being called by the planner (see `PlanPolicy`/`ToolExecutionPolicy`
    blocked tool lists), so eagerly building the parsing/classification/
    extraction pipeline (Docling parser, extraction LLM service, etc.) for
    every agent session would be pure startup cost paid on a path that
    almost never runs. This proxy duck-types the two methods
    `IngestDocumentTool.run`/`ReingestDocumentTool.run` actually call, and is
    shared by both tools so the underlying `IngestionWorkflow` is only ever
    built once regardless of which tool triggers the build.
    """

    def __init__(
        self,
        *,
        unit_of_work: Any,
        vector_store: Any,
        qdrant_client: Any,
        embedding_provider: Any,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._vector_store = vector_store
        self._qdrant_client = qdrant_client
        self._embedding_provider = embedding_provider
        self._ingestion_workflow: Any = None

    def run(self, request: Any) -> Any:
        return self._resolve().run(request)

    def reingest(self, request: Any) -> Any:
        return self._resolve().reingest(request)

    def _resolve(self) -> Any:
        if self._ingestion_workflow is None:
            from src.application.orchestrator.ingestion import (
                build_ingestion_runtime,
            )

            runtime = build_ingestion_runtime(
                unit_of_work=self._unit_of_work,
                vector_store=self._vector_store,
                qdrant_client=self._qdrant_client,
                embedding_provider=self._embedding_provider,
                bootstrap=False,
            )
            self._ingestion_workflow = runtime.ingestion_workflow
        return self._ingestion_workflow


@dataclass(slots=True)
class DemoRuntimeStatus:
    document_count: int = 0
    embedding_index_status: str = "Ready"
    model_name: str | None = None
    capabilities: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AgentRuntime:
    graph: Any
    session: Any = None
    qdrant_client: Any = None
    conversation_memory: Any = None
    session_state_store: Any = None
    document_catalog_service: Any = None
    runtime_status: DemoRuntimeStatus = field(default_factory=DemoRuntimeStatus)
    runtime_settings: dict[str, Any] = field(default_factory=dict)

    def run_graph_request(
        self,
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
        event_sink: Any = None,
    ) -> GraphResult:
        return self.graph.run(
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
            event_sink=event_sink,
        )

    def load_session_snapshot(self, session_id: str | None) -> dict[str, Any]:
        if self.conversation_memory is None:
            return {}
        snapshot = self.conversation_memory.load_session(session_id)
        if isinstance(snapshot, dict):
            return snapshot
        return {}

    def clear_persisted_session(self, session_id: str | None) -> None:
        if self.conversation_memory is None or not session_id:
            return
        self.conversation_memory.clear(session_id)


def build_agent_runtime(
    session,
    *,
    enable_generation: bool,
    enable_llm_planning: bool,
    enable_llm_research_planning: bool,
) -> AgentRuntime:
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
        QueryScopeGuardrail,
        RetrievalEvidenceGuardrail,
    )
    from src.application.langgraph import (
        ClarificationBuilder,
        ConversationMemory,
        EvidenceMerger,
        GraphFactory,
        LLMResearchPlanner,
        NodeFactory,
        ReflectionJsonParser,
        ReflectionPolicy,
        ReflectionService,
        ReflectionValidator,
        ResearchPolicy,
        RetryQueryBuilder,
        RetrievalRetryPolicy,
        SessionStateStore,
        ToolRegistry,
    )
    from src.application.langgraph.planning import (
        LLMPlanProposer,
        PlanParser,
        PlanPolicy,
        PlanRepair,
        PlanValidator,
    )
    from src.application.langgraph.retrieval_strategy import (
        LLMStrategySelector,
        RetrievalPlanExecutor,
        RetrievalStrategyPolicy,
        RetrievalStrategyService,
        StrategyRetryPolicy,
    )
    from src.application.langgraph.strategy_advisor.advisor import StrategyAdvisor
    from src.application.orchestrator.retrieval import build_retrieval_runtime
    from src.application.prompts.reflection import ReflectionPromptBuilder
    from src.application.services.ai import LLMService
    from src.application.services.answer_generation import AnswerGenerationService
    from src.application.services.document import DocumentCatalogService
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
    from src.application.tools.ingestion import (
        DeleteDocumentTool,
        IngestDocumentTool,
        ReingestDocumentTool,
    )
    from src.application.tools.question_answering import AnswerQuestionTool
    from src.application.tools.retrieval import (
        RetrieveChunksTool,
        RetrieveFiguresTool,
        RetrieveIdentifiersTool,
        RetrieveTablesTool,
    )
    from src.application.workflows.ingestion import DeleteDocumentWorkflow
    from src.application.workflows.question_answering import (
        QuestionAnsweringRouter,
        QuestionAnsweringWorkflow,
    )
    from src.config.settings import (
        ingestion_settings,
        langgraph_settings,
        llm_settings,
    )
    from src.infrastructure.ai.llm import OllamaLLMProvider
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

    uow = SqlAlchemyUnitOfWork(session)
    retrieval_runtime = build_retrieval_runtime(
        unit_of_work=uow,
        pre_retrieval_guardrails=[QueryScopeGuardrail()],
        post_retrieval_guardrails=[
            DocumentRelevanceGuardrail(),
            RetrievalEvidenceGuardrail(),
        ],
    )
    embedding_provider = retrieval_runtime.embedding_provider
    qdrant_client = retrieval_runtime.qdrant_client
    vector_store = retrieval_runtime.vector_store
    document_catalog_service = DocumentCatalogService(uow.documents)
    document_lookup_service = retrieval_runtime.document_lookup_service
    retrieval_workflow = retrieval_runtime.retrieval_workflow
    exploration_service = retrieval_runtime.exploration_service

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
    strategy_advisor = StrategyAdvisor(
        retrieval_strategy_llm_service,
        model=retrieval_strategy_model,
    )

    qa_workflow = QuestionAnsweringWorkflow(
        retrieval_workflow=retrieval_workflow,
        exploration_service=exploration_service,
        router=QuestionAnsweringRouter(),
        pre_query_guardrails=[QueryScopeGuardrail()],
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
    delete_document_workflow = DeleteDocumentWorkflow(
        unit_of_work=uow,
        vector_store=vector_store,
    )
    lazy_ingestion_workflow = _LazyIngestionWorkflow(
        unit_of_work=uow,
        vector_store=vector_store,
        qdrant_client=qdrant_client,
        embedding_provider=embedding_provider,
    )
    ingest_document_tool = IngestDocumentTool(lazy_ingestion_workflow)
    reingest_document_tool = ReingestDocumentTool(lazy_ingestion_workflow)
    delete_document_tool = DeleteDocumentTool(delete_document_workflow)
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
        ingest_document_tool=ingest_document_tool,
        reingest_document_tool=reingest_document_tool,
        delete_document_tool=delete_document_tool,
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
            strategy_advisor=strategy_advisor,
            policy=retrieval_strategy_policy,
        ),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=retrieval_strategy_policy,
        strategy_retry_policy=StrategyRetryPolicy(),
        strategy_advisor=strategy_advisor,
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
    session_state_store = SessionStateStore()
    conversation_memory = ConversationMemory(
        max_messages=20,
        session_state_store=session_state_store,
    )
    graph = GraphFactory(node_factory=node_factory).create_document_agent_graph(
        tool_registry=tool_registry,
        memory=conversation_memory,
    )
    runtime_status = DemoRuntimeStatus(
        document_count=len(document_catalog_service.list_documents()),
        embedding_index_status="Ready",
        model_name=llm_settings.general_llm,
        capabilities=[
            "Question Answering",
            "Retrieval-Augmented Generation",
            "Deep Research",
            "Multi-step Planning",
            "Reflection",
            "Retrieval Strategy Selection",
            "Safe Grounded Answers",
        ],
    )
    return AgentRuntime(
        graph=graph,
        session=session,
        qdrant_client=qdrant_client,
        conversation_memory=conversation_memory,
        session_state_store=session_state_store,
        document_catalog_service=document_catalog_service,
        runtime_status=runtime_status,
        runtime_settings={
            "ollama_base_url": llm_settings.ollama_base_url,
            "general_llm": llm_settings.general_llm,
            "planning_llm": llm_settings.planning_llm or llm_settings.general_llm,
            "answer_generation_llm": llm_settings.answer_generation_llm,
            "deep_research_enabled": langgraph_settings.deep_research_enabled,
            "reflection_enabled": langgraph_settings.reflection_enabled,
            "retrieval_strategy_enabled": langgraph_settings.retrieval_strategy_enabled,
            "generation_enabled": enable_generation or ingestion_settings.enable_answer_generation,
        },
    )


def close_agent_runtime(runtime: AgentRuntime | None) -> None:
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
