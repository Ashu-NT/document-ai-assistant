from __future__ import annotations

from typing import Any

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalExecutionResult,
    RetrievalPlan,
)
from src.application.langgraph.retrieval_strategy.services import RetrievalEvidenceMerger
from src.application.tools.retrieval import (
    RetrieveChunksRequest,
    RetrieveFiguresRequest,
    RetrieveIdentifiersRequest,
    RetrieveTablesRequest,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class RetrievalPlanExecutor:
    def __init__(
        self,
        *,
        evidence_merger: RetrievalEvidenceMerger | None = None,
    ) -> None:
        self.evidence_merger = evidence_merger or RetrievalEvidenceMerger()

    def execute(
        self,
        plan: RetrievalPlan,
        *,
        tool_registry: ToolRegistry,
        max_chunks: int,
    ) -> RetrievalExecutionResult:
        step_results: dict[str, Any] = {}
        collected_chunks: list[RetrievedChunk] = []
        errors: list[str] = []
        tool_names: list[str] = []

        for step in plan.steps:
            tool = tool_registry.require(step.tool_name)
            request = self._build_request(step.tool_name, step.args)
            result = tool.run(request)
            tool_names.append(step.tool_name)
            step_results[step.step_id] = self._serialize_tool_result(result)
            if not result.success:
                errors.append(result.error_code or f"{step.step_id}_failed")
                if step.required:
                    return RetrievalExecutionResult(
                        plan=plan,
                        success=False,
                        step_results=serialize_graph_value(step_results),
                        evidence_chunks=[],
                        context_document_ids=[],
                        tool_names=tool_names,
                        errors=errors,
                        diagnostics={"failed_step": step.step_id},
                    )
                continue

            chunks = self._extract_chunks(result.data)
            for chunk in chunks:
                chunk.metadata["retrieval_strategy"] = step.strategy.value
                chunk.metadata["retrieval_step_id"] = step.step_id
            collected_chunks.extend(chunks)

        merged = self.evidence_merger.merge(
            chunks=collected_chunks,
            primary_strategy=plan.primary_strategy,
            max_chunks=max_chunks,
        )
        document_ids = self._context_document_ids(merged)
        return RetrievalExecutionResult(
            plan=plan,
            success=bool(merged or not errors),
            step_results=serialize_graph_value(step_results),
            evidence_chunks=merged,
            context_document_ids=document_ids,
            tool_names=tool_names,
            errors=errors,
            diagnostics={
                "raw_evidence_count": len(collected_chunks),
                "merged_evidence_count": len(merged),
            },
        )

    @staticmethod
    def _build_request(tool_name: str, args: dict[str, Any]) -> object:
        if tool_name == "retrieve_chunks":
            return RetrieveChunksRequest(
                query_text=str(args.get("query_text") or ""),
                document_id=args.get("document_id"),
                top_k=int(args.get("top_k") or 5),
                chunk_types=list(args.get("chunk_types", [])),
            )
        if tool_name == "retrieve_tables":
            return RetrieveTablesRequest(
                query_text=str(args.get("query_text") or ""),
                document_id=args.get("document_id"),
                top_k=int(args.get("top_k") or 5),
            )
        if tool_name == "retrieve_identifiers":
            return RetrieveIdentifiersRequest(
                query_text=str(args.get("query_text") or ""),
                document_id=args.get("document_id"),
                top_k=int(args.get("top_k") or 5),
            )
        if tool_name == "retrieve_figures":
            return RetrieveFiguresRequest(
                query_text=str(args.get("query_text") or ""),
                document_id=args.get("document_id"),
                top_k=int(args.get("top_k") or 5),
            )
        raise ValueError(f"Unsupported retrieval plan tool: {tool_name}")

    @staticmethod
    def _extract_chunks(data: Any) -> list[RetrievedChunk]:
        if not isinstance(data, dict):
            return []
        context_chunks = data.get("context_chunks")
        if isinstance(context_chunks, list):
            return [chunk for chunk in context_chunks if isinstance(chunk, RetrievedChunk)]
        chunks = data.get("chunks")
        if isinstance(chunks, list):
            return [chunk for chunk in chunks if isinstance(chunk, RetrievedChunk)]
        return []

    @staticmethod
    def _context_document_ids(chunks: list[RetrievedChunk]) -> list[str]:
        document_ids: list[str] = []
        seen: set[str] = set()
        for chunk in chunks:
            if chunk.document_id in seen:
                continue
            seen.add(chunk.document_id)
            document_ids.append(chunk.document_id)
        return document_ids

    @staticmethod
    def _serialize_tool_result(result: Any) -> dict[str, Any]:
        return serialize_graph_value(
            {
                "success": bool(getattr(result, "success", False)),
                "message": getattr(result, "message", None),
                "error_code": getattr(result, "error_code", None),
                "diagnostics": getattr(result, "diagnostics", {}) or {},
                "metadata": getattr(result, "metadata", None),
                "data": getattr(result, "data", None),
            }
        )
