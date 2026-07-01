from __future__ import annotations

from src.application.langgraph.common import GraphError

from src.application.langgraph.research.models import (
    ResearchEvidence,
    ResearchTaskResult,
)
from src.application.langgraph.retrieval_strategy import RetrievalContext
from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy
from src.shared.ids import IdGenerator


class ResearchTaskExecutor:
    def __init__(
        self,
        *,
        retrieval_strategy_service=None,
        retrieval_plan_executor=None,
        id_generator: IdGenerator | None = None,
    ) -> None:
        self.retrieval_strategy_service = retrieval_strategy_service
        self.retrieval_plan_executor = retrieval_plan_executor
        self.id_generator = id_generator or IdGenerator()

    def execute(
        self,
        task,
        *,
        route: str,
        document_title: str | None,
        tool_registry,
        use_llm_strategy: bool,
    ) -> ResearchTaskResult:
        if self.retrieval_strategy_service is None or self.retrieval_plan_executor is None:
            return ResearchTaskResult(
                task_id=task.task_id,
                success=False,
                errors=["research_retrieval_not_configured"],
            )

        requested_strategy = None
        if task.strategy_hint:
            requested_strategy = RetrievalStrategy(task.strategy_hint)

        context = RetrievalContext(
            query_text=task.question,
            route=route,
            document_id=task.document_id,
            document_title=document_title,
            top_k=task.max_results,
            answer_intent=task.answer_intent_hint,
            requested_strategy=requested_strategy,
            use_llm_selector=use_llm_strategy,
        )
        try:
            strategy_result = self.retrieval_strategy_service.select_and_plan(
                context,
                tool_registry=tool_registry,
            )
            execution_result = self.retrieval_plan_executor.execute(
                strategy_result.plan,
                tool_registry=tool_registry,
                max_chunks=task.max_results,
            )
        except GraphError as exc:
            return ResearchTaskResult(
                task_id=task.task_id,
                success=False,
                errors=[exc.error_code or "research_task_execution_failed"],
                diagnostics=exc.details or {},
            )
        evidence = [
            ResearchEvidence(
                evidence_id=self.id_generator.new_id("research_evidence"),
                task_id=task.task_id,
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_title=document_title,
                section_path=list(chunk.section_path),
                page_start=chunk.source.page_start,
                page_end=chunk.source.page_end,
                chunk_type=chunk.chunk_type.value if chunk.chunk_type is not None else None,
                score=chunk.score,
                content_excerpt=_preview_text(chunk.content),
                source_tool=chunk.retrieval_source,
                diagnostics=dict(chunk.metadata),
            )
            for chunk in execution_result.evidence_chunks
        ]
        return ResearchTaskResult(
            task_id=task.task_id,
            success=execution_result.success,
            tool_names=list(execution_result.tool_names),
            retrieval_strategy=strategy_result.decision.primary_strategy.value,
            evidence=evidence,
            errors=list(execution_result.errors),
            diagnostics={
                "concept": getattr(task, "diagnostics", {}).get("concept"),
                "concept_role": getattr(task, "diagnostics", {}).get("concept_role"),
                "retrieval_plan": strategy_result.plan.to_dict(),
                "retrieval_trace": strategy_result.trace,
                "execution_result": execution_result.to_dict(),
            },
        )


def _preview_text(value: str, *, limit: int = 400) -> str:
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
