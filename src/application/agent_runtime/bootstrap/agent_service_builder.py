from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AgentServices:
    uow: Any
    embedding_provider: Any
    qdrant_client: Any
    vector_store: Any
    document_catalog_service: Any
    extraction_service: Any
    document_lookup_service: Any
    retrieval_workflow: Any
    exploration_service: Any
    qa_workflow: Any
    planning_llm_service: Any
    reflection_llm_service: Any
    reflection_model: str | None
    strategy_advisor: Any


def build_agent_services(
    session,
    *,
    enable_generation: bool,
    enable_llm_planning: bool,
    enable_llm_research_planning: bool,
) -> AgentServices:
    from src.application.guardrails.answering import (
        AnswerSupportGuardrail,
        CitationGuardrail,
        ConflictingEvidenceGuardrail,
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
    from src.application.langgraph.strategy_advisor.advisor import StrategyAdvisor
    from src.application.orchestrator.retrieval import build_retrieval_runtime
    from src.application.services.ai import LLMService
    from src.application.services.answer_generation import AnswerGenerationService
    from src.application.services.document import DocumentCatalogService
    from src.application.services.extraction import ExtractionService
    from src.application.validation.extraction import ExtractionResultValidator
    from src.application.workflows.question_answering import (
        QuestionAnsweringRouter,
        QuestionAnsweringWorkflow,
    )
    from src.config.settings import llm_settings
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
    extraction_service = ExtractionService(
        extraction_repository=uow.extractions,
        extraction_result_validator=ExtractionResultValidator(),
    )
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
                ConflictingEvidenceGuardrail(),
                CitationGuardrail(),
                UnsupportedClaimGuardrail(),
                UnsupportedSuggestionGuardrail(),
                AnswerSupportGuardrail(),
            ]
            if enable_generation
            else []
        ),
        document_lookup_service=document_lookup_service,
        structured_evidence_resolver=retrieval_workflow.structured_evidence_resolver,
    )

    return AgentServices(
        uow=uow,
        embedding_provider=embedding_provider,
        qdrant_client=qdrant_client,
        vector_store=vector_store,
        document_catalog_service=document_catalog_service,
        extraction_service=extraction_service,
        document_lookup_service=document_lookup_service,
        retrieval_workflow=retrieval_workflow,
        exploration_service=exploration_service,
        qa_workflow=qa_workflow,
        planning_llm_service=planning_llm_service,
        reflection_llm_service=reflection_llm_service,
        reflection_model=reflection_model,
        strategy_advisor=strategy_advisor,
    )
