from __future__ import annotations

from typing import Any

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.graphs.document_agent.document_agent_answer_extractor import (
    tool_payload,
)


def extract_context_chunks(
    *,
    tool_results: dict[str, Any],
    citations: list[dict[str, Any]],
    fallback_document_title: str | None,
    selected_document_id: str | None,
) -> list[dict[str, Any]]:
    approved_chunk_ids: set[str] = set()
    rejected_chunk_ids: set[str] = set()

    answer_question_payload = tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        approved_chunk_ids = set(answer_question_payload.get("approved_chunk_ids", []))
        rejected_chunk_ids = set(answer_question_payload.get("rejected_chunk_ids", []))
        retrieval_workflow_result = answer_question_payload.get("retrieval_result")
        if isinstance(retrieval_workflow_result, dict):
            context_chunks = retrieval_workflow_result.get("context_chunks")
            if isinstance(context_chunks, list):
                return _enrich_context_chunks(
                    context_chunks,
                    citations=citations,
                    fallback_document_title=fallback_document_title,
                    selected_document_id=selected_document_id,
                    approved_chunk_ids=approved_chunk_ids,
                    rejected_chunk_ids=rejected_chunk_ids,
                )

    retrieve_evidence_payload = tool_payload(tool_results, "retrieve_evidence")
    if isinstance(retrieve_evidence_payload, dict):
        context_chunks = retrieve_evidence_payload.get("context_chunks")
        if isinstance(context_chunks, list):
            return _enrich_context_chunks(
                context_chunks,
                citations=citations,
                fallback_document_title=fallback_document_title,
                selected_document_id=selected_document_id,
                approved_chunk_ids=approved_chunk_ids,
                rejected_chunk_ids=rejected_chunk_ids,
            )

    return []


def _enrich_context_chunks(
    context_chunks: list[dict[str, Any]],
    *,
    citations: list[dict[str, Any]],
    fallback_document_title: str | None,
    selected_document_id: str | None,
    approved_chunk_ids: set[str],
    rejected_chunk_ids: set[str],
) -> list[dict[str, Any]]:
    citation_by_chunk_id = {
        citation.get("chunk_id"): citation
        for citation in citations
        if isinstance(citation, dict) and citation.get("chunk_id")
    }

    enriched_chunks: list[dict[str, Any]] = []
    for chunk in context_chunks:
        if not isinstance(chunk, dict):
            continue

        enriched_chunk = dict(chunk)
        chunk_id = str(enriched_chunk.get("chunk_id") or "")
        citation = citation_by_chunk_id.get(chunk_id)
        embedded_citation = enriched_chunk.get("citation")
        if isinstance(embedded_citation, dict) and citation is None:
            citation = embedded_citation

        document_id = enriched_chunk.get("document_id")
        document_title = None
        section_title = None
        if isinstance(citation, dict):
            document_title = citation.get("document_name")
            section_title = citation.get("section_title")

        if document_title is None and selected_document_id and document_id == selected_document_id:
            document_title = fallback_document_title

        if section_title is None:
            section_path = enriched_chunk.get("section_path") or []
            if isinstance(section_path, list) and section_path:
                section_title = section_path[-1]

        enriched_chunk["document_title"] = document_title
        enriched_chunk["section_title"] = section_title
        enriched_chunk["approved"] = chunk_id in approved_chunk_ids if approved_chunk_ids else None
        enriched_chunk["rejected"] = chunk_id in rejected_chunk_ids if rejected_chunk_ids else None
        enriched_chunks.append(serialize_graph_value(enriched_chunk))

    return enriched_chunks
