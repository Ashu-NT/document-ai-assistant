from __future__ import annotations

from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorIntent,
    StrategyAdvisorRequest,
)


class StrategyAdvisorPromptBuilder:
    def build(self, request: StrategyAdvisorRequest) -> str:
        from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
            RetrievalStrategy,
        )

        intent_list = ", ".join(intent.value for intent in StrategyAdvisorIntent)
        strategy_list = ", ".join(
            strategy.value
            for strategy in RetrievalStrategy
            if strategy != RetrievalStrategy.MULTI_STRATEGY
        )
        route_list = ", ".join(request.allowed_routes or ["answer_question", "deep_research"])
        deterministic_strategies = (
            ", ".join(strategy.value for strategy in request.deterministic_strategies)
            or "-"
        )
        signal_lines = [f"- {signal}" for signal in request.signals] or ["- none"]
        return "\n".join(
            [
                "You are a guarded strategy advisor for a document AI assistant.",
                "You advise only. The system validates and decides.",
                "",
                f"User query: {request.query_text}",
                f"Deterministic route: {request.deterministic_route or '-'}",
                f"Deterministic route confidence: {request.deterministic_route_confidence:.2f}",
                f"Deterministic reason: {request.deterministic_reason or '-'}",
                f"Deterministic strategies: {deterministic_strategies}",
                f"Selected document id: {request.selected_document_id or '-'}",
                f"Selected document title: {request.selected_document_title or '-'}",
                f"Trigger reason: {request.trigger_reason or '-'}",
                "",
                "Detected deterministic signals:",
                *signal_lines,
                "",
                f"Allowed intents: {intent_list}",
                f"Allowed routes: {route_list}",
                f"Allowed strategies: {strategy_list}",
                "",
                "Rules:",
                "- Never answer the user.",
                "- Never cite documents.",
                "- Never invent tools, workflows, routes, intents, or strategies.",
                "- Use only concepts that are explicitly present in the user query.",
                "- Preserve all distinct user concepts instead of collapsing them.",
                "- Recommend multiple strategies when the query spans multiple concepts.",
                "- Return JSON only.",
                "",
                "Return this schema exactly:",
                "{",
                '  "intent": "comparison",',
                '  "route": "deep_research",',
                '  "confidence": 0.92,',
                '  "concepts": ["troubleshooting", "maintenance", "procedures"],',
                '  "recommended_strategies": [',
                '    "TROUBLESHOOTING_LOOKUP",',
                '    "MAINTENANCE_LOOKUP",',
                '    "PROCEDURE_LOOKUP"',
                "  ],",
                '  "comparison": true,',
                '  "requires_table": true,',
                '  "reason": "User is requesting comparison of multiple maintenance-related concepts."',
                "}",
            ]
        )
