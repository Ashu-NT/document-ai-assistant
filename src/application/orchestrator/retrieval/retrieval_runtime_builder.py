from __future__ import annotations

from src.application.contracts import UnitOfWork
from src.application.contracts.ai import EmbeddingProvider
from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.orchestrator.ingestion.vector_runtime_builder import (
    build_vector_store,
)
from src.application.orchestrator.retrieval.retrieval_runtime import RetrievalRuntime
from src.application.services.document import DocumentLookupService
from src.application.services.document_exploration import DocumentExplorationService
from src.application.services.retrieval import HybridRetrievalService
from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval import (
    RetrievalContextExpander,
    RetrievalWorkflow,
)
from src.infrastructure.ai.embeddings import create_embedding_provider
from src.infrastructure.retrieval.keyword import SqlKeywordIndex
from src.infrastructure.retrieval.rerankers import DeterministicHybridReranker
from src.shared.ids import IdGenerator


def build_retrieval_runtime(
    *,
    unit_of_work: UnitOfWork,
    embedding_provider: EmbeddingProvider | None = None,
    pre_retrieval_guardrails: list[Guardrail] | None = None,
    post_retrieval_guardrails: list[Guardrail] | None = None,
) -> RetrievalRuntime:
    """Build the SQL+dense hybrid retrieval stack.

    This wiring was previously re-derived near-verbatim in three places
    (`build_agent_runtime`, `ask_document.py::build_qa_runtime`,
    `run_retrieval_benchmark.py::build_benchmark_runtime`) — this is now the
    single place it's assembled.

    `pre_retrieval_guardrails`/`post_retrieval_guardrails` have no built-in
    default and are passed straight through to `RetrievalWorkflow`, since
    callers genuinely differ here: interactive/CLI callers want guardrails
    applied, but the retrieval benchmark deliberately runs without them so
    it scores raw retrieval quality rather than guardrail-filtered results.

    `embedding_provider` is an optional escape hatch for a caller that
    already has one open (mirrors `build_ingestion_runtime`'s equivalent
    parameters) — omit it to build a fresh one.
    """
    resolved_embedding_provider = embedding_provider or create_embedding_provider()
    vector_store, qdrant_client = build_vector_store(
        unit_of_work=unit_of_work,
        embedding_provider=resolved_embedding_provider,
    )
    query_validator = RetrievalQueryValidator()
    document_lookup_service = DocumentLookupService(unit_of_work.documents)
    retrieval_service = HybridRetrievalService(
        keyword_index=SqlKeywordIndex(unit_of_work.keyword_index),
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
        pre_retrieval_guardrails=list(pre_retrieval_guardrails or []),
        post_retrieval_guardrails=list(post_retrieval_guardrails or []),
    )
    return RetrievalRuntime(
        retrieval_workflow=retrieval_workflow,
        document_lookup_service=document_lookup_service,
        exploration_service=DocumentExplorationService(document_lookup_service),
        vector_store=vector_store,
        qdrant_client=qdrant_client,
        embedding_provider=resolved_embedding_provider,
    )
