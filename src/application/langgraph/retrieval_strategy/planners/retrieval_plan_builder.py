from __future__ import annotations

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalPlan,
    RetrievalPlanStep,
    RetrievalStrategy,
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)
from src.domain.common import ChunkType, new_id


class RetrievalPlanBuilder:
    def build(
        self,
        decision: RetrievalStrategyDecision,
        *,
        tool_registry: ToolRegistry,
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalPlan:
        strategies = decision.selected_strategies[: policy.max_strategies_per_query]
        if not strategies:
            strategies = [policy.default_strategy]

        steps = [
            self._build_step(
                index=index,
                strategy=strategy,
                decision=decision,
                tool_registry=tool_registry,
            )
            for index, strategy in enumerate(strategies, start=1)
        ]
        return RetrievalPlan(
            plan_id=new_id("rplan"),
            original_query=decision.query,
            document_id=decision.document_id,
            steps=steps,
            primary_strategy=decision.primary_strategy,
            reason=decision.reason,
            diagnostics={"strategy_count": len(steps)},
        )

    def _build_step(
        self,
        *,
        index: int,
        strategy: RetrievalStrategy,
        decision: RetrievalStrategyDecision,
        tool_registry: ToolRegistry,
    ) -> RetrievalPlanStep:
        tool_name = self._tool_name_for(strategy, tool_registry)
        query = self._query_for(strategy, decision)
        chunk_types = self._chunk_types_for(strategy)
        return RetrievalPlanStep(
            step_id=f"retrieval_step_{index}",
            strategy=strategy,
            query=query,
            document_id=decision.document_id,
            top_k=decision.top_k,
            tool_name=tool_name,
            args={
                "query_text": query,
                "document_id": decision.document_id,
                "top_k": decision.top_k,
                "chunk_types": chunk_types,
            },
            output_key=f"retrieval_{index}",
            required=index == 1,
            reason=f"Execute {strategy.value} using {tool_name}.",
        )

    @staticmethod
    def _tool_name_for(
        strategy: RetrievalStrategy,
        tool_registry: ToolRegistry,
    ) -> str:
        if strategy == RetrievalStrategy.IDENTIFIER_LOOKUP and tool_registry.maybe(
            "retrieve_identifiers"
        ):
            return "retrieve_identifiers"
        if strategy == RetrievalStrategy.TABLE_LOOKUP and tool_registry.maybe(
            "retrieve_tables"
        ):
            return "retrieve_tables"
        if strategy in {
            RetrievalStrategy.DRAWING_LOOKUP,
            RetrievalStrategy.FIGURE_LOOKUP,
        } and tool_registry.maybe("retrieve_figures"):
            return "retrieve_figures"
        return "retrieve_chunks"

    @staticmethod
    def _query_for(
        strategy: RetrievalStrategy,
        decision: RetrievalStrategyDecision,
    ) -> str:
        base = decision.rewritten_query or decision.query
        expansion = {
            RetrievalStrategy.IDENTIFIER_LOOKUP: "identifier part number serial number order code model",
            RetrievalStrategy.TECHNICAL_SPECIFICATION: "technical specification technical data values pressure temperature rating",
            RetrievalStrategy.TABLE_LOOKUP: "table list schedule matrix values rows columns",
            RetrievalStrategy.SECTION_LOOKUP: "section heading chapter page appendix path",
            RetrievalStrategy.MAINTENANCE_LOOKUP: "maintenance service interval inspection schedule lubrication",
            RetrievalStrategy.PROCEDURE_LOOKUP: "procedure steps install replace operate commission start stop",
            RetrievalStrategy.TROUBLESHOOTING_LOOKUP: "troubleshooting fault error cause remedy problem",
            RetrievalStrategy.CERTIFICATION_LOOKUP: "certificate approval inspection compliance issued valid",
            RetrievalStrategy.DRAWING_LOOKUP: "drawing diagram schematic layout dimensions view",
            RetrievalStrategy.FIGURE_LOOKUP: "figure image picture diagram view",
            RetrievalStrategy.DOCUMENT_EXPLORATION: "overview sections structure contents",
            RetrievalStrategy.GENERAL_HYBRID: "",
            RetrievalStrategy.MULTI_STRATEGY: "",
        }.get(strategy, "")
        return " ".join(part for part in (base, expansion) if part).strip()

    @staticmethod
    def _chunk_types_for(strategy: RetrievalStrategy) -> list[ChunkType]:
        mapping = {
            RetrievalStrategy.IDENTIFIER_LOOKUP: [
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.SPARE_PARTS_TABLE,
                ChunkType.CERTIFICATION_INFO,
                ChunkType.DRAWING_REFERENCE,
            ],
            RetrievalStrategy.TECHNICAL_SPECIFICATION: [
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.CERTIFICATION_INFO,
                ChunkType.SPARE_PARTS_TABLE,
            ],
            RetrievalStrategy.TABLE_LOOKUP: [
                ChunkType.SPARE_PARTS_TABLE,
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.CERTIFICATION_INFO,
            ],
            RetrievalStrategy.SECTION_LOOKUP: [
                ChunkType.OVERVIEW,
                ChunkType.GENERAL,
            ],
            RetrievalStrategy.MAINTENANCE_LOOKUP: [
                ChunkType.MAINTENANCE_INTERVAL,
                ChunkType.MAINTENANCE_PROCEDURE,
                ChunkType.OPERATION_INSTRUCTION,
                ChunkType.GENERAL,
            ],
            RetrievalStrategy.PROCEDURE_LOOKUP: [
                ChunkType.OPERATION_INSTRUCTION,
                ChunkType.MAINTENANCE_PROCEDURE,
                ChunkType.INSTALLATION_INSTRUCTION,
                ChunkType.GENERAL,
            ],
            RetrievalStrategy.TROUBLESHOOTING_LOOKUP: [
                ChunkType.TROUBLESHOOTING,
                ChunkType.OPERATION_INSTRUCTION,
                ChunkType.GENERAL,
            ],
            RetrievalStrategy.CERTIFICATION_LOOKUP: [
                ChunkType.CERTIFICATION_INFO,
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.GENERAL,
            ],
            RetrievalStrategy.DRAWING_LOOKUP: [
                ChunkType.DRAWING_REFERENCE,
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.GENERAL,
            ],
            RetrievalStrategy.FIGURE_LOOKUP: [
                ChunkType.DRAWING_REFERENCE,
                ChunkType.GENERAL,
            ],
            RetrievalStrategy.DOCUMENT_EXPLORATION: [
                ChunkType.OVERVIEW,
                ChunkType.GENERAL,
            ],
        }
        return list(mapping.get(strategy, []))
