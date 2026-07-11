from __future__ import annotations

from typing import Any

from src.application.agent_runtime.bootstrap.agent_service_builder import AgentServices
from src.application.agent_runtime.bootstrap.lazy_ingestion_workflow import (
    _LazyIngestionWorkflow,
)


def build_agent_tool_registry(services: AgentServices) -> Any:
    from src.application.langgraph import ToolRegistry
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
        RetrieveStructuredEntitiesTool,
        RetrieveTablesTool,
    )
    from src.application.workflows.ingestion import DeleteDocumentWorkflow

    document_catalog_service = services.document_catalog_service
    exploration_service = services.exploration_service
    retrieval_workflow = services.retrieval_workflow
    extraction_service = services.extraction_service

    find_document_tool = FindDocumentTool(document_catalog_service)
    retrieve_chunks_tool = RetrieveChunksTool(retrieval_workflow)
    retrieve_tables_tool = RetrieveTablesTool(
        retrieve_chunks_tool,
        exploration_service,
    )
    retrieve_identifiers_tool = RetrieveIdentifiersTool(
        services.document_lookup_service,
        exploration_service,
        retrieve_chunks_tool,
    )
    retrieve_structured_entities_tool = RetrieveStructuredEntitiesTool(
        extraction_service,
        entity_resolver=(
            retrieval_workflow.structured_evidence_resolver.entity_resolver
            if retrieval_workflow.structured_evidence_resolver is not None
            else None
        ),
    )
    retrieve_figures_tool = RetrieveFiguresTool(
        retrieve_chunks_tool,
        exploration_service,
    )
    delete_document_workflow = DeleteDocumentWorkflow(
        unit_of_work=services.uow,
        vector_store=services.vector_store,
    )
    lazy_ingestion_workflow = _LazyIngestionWorkflow(
        unit_of_work=services.uow,
        vector_store=services.vector_store,
        qdrant_client=services.qdrant_client,
        embedding_provider=services.embedding_provider,
    )
    ingest_document_tool = IngestDocumentTool(lazy_ingestion_workflow)
    reingest_document_tool = ReingestDocumentTool(lazy_ingestion_workflow)
    delete_document_tool = DeleteDocumentTool(delete_document_workflow)
    return ToolRegistry(
        list_documents_tool=ListDocumentsTool(document_catalog_service),
        find_document_tool=find_document_tool,
        document_details_tool=DocumentDetailsTool(document_catalog_service),
        explore_document_tool=ExploreDocumentTool(exploration_service),
        retrieve_chunks_tool=retrieve_chunks_tool,
        retrieve_tables_tool=retrieve_tables_tool,
        retrieve_identifiers_tool=retrieve_identifiers_tool,
        retrieve_structured_entities_tool=retrieve_structured_entities_tool,
        retrieve_figures_tool=retrieve_figures_tool,
        answer_question_tool=AnswerQuestionTool(
            services.qa_workflow,
            find_document_tool=find_document_tool,
        ),
        run_quality_gate_tool=RunQualityGateTool(),
        retrieval_trace_tool=RetrievalTraceTool(retrieval_workflow),
        ingest_document_tool=ingest_document_tool,
        reingest_document_tool=reingest_document_tool,
        delete_document_tool=delete_document_tool,
    )
