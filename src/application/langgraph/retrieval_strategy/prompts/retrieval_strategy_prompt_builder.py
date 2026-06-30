from __future__ import annotations

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
    RetrievalStrategySignal,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)
from src.application.langgraph.retrieval_strategy.prompts.retrieval_strategy_prompt_version import (
    RETRIEVAL_STRATEGY_PROMPT_VERSION,
)


class RetrievalStrategyPromptBuilder:
    def build(
        self,
        *,
        context: RetrievalContext,
        signals: list[RetrievalStrategySignal],
        policy: RetrievalStrategyPolicy,
    ) -> str:
        strategy_list = ", ".join(strategy.value for strategy in RetrievalStrategy)
        signal_lines = [
            f"- {signal.category}: {signal.value} ({signal.score:.2f})"
            for signal in signals
        ] or ["- none"]
        return "\n".join(
            [
                "You are selecting a retrieval strategy for a document agent.",
                f"Prompt version: {RETRIEVAL_STRATEGY_PROMPT_VERSION}",
                "",
                f"Question: {context.query_text}",
                f"Selected document id: {context.effective_document_id or '-'}",
                f"Selected document title: {context.effective_document_title or '-'}",
                f"Route: {context.route or '-'}",
                f"Answer intent: {context.answer_intent or '-'}",
                f"Retry reason: {context.retry_reason or '-'}",
                "",
                "Allowed strategies:",
                strategy_list,
                "",
                "Detected signals:",
                *signal_lines,
                "",
                "Policy:",
                f"- max_strategies_per_query: {policy.max_strategies_per_query}",
                f"- default_top_k: {policy.default_top_k}",
                f"- max_top_k: {policy.max_top_k}",
                f"- preserve_document_scope: {policy.preserve_document_scope}",
                "",
                "Rules:",
                "- Return JSON only.",
                "- Select from allowed strategies only.",
                "- Do not invent strategies.",
                "- If uncertain, choose GENERAL_HYBRID.",
                "- If multiple evidence types are required, set primary_strategy to MULTI_STRATEGY and list ordered secondary_strategies.",
                "- Preserve document scope.",
                "",
                "Example JSON:",
                '{',
                '  "primary_strategy": "TECHNICAL_SPECIFICATION",',
                '  "secondary_strategies": ["TABLE_LOOKUP"],',
                '  "confidence": 0.87,',
                '  "reason": "The question asks for pressure and design values.",',
                '  "rewritten_query": "test pressure design pressure technical data",',
                '  "top_k": 8',
                '}',
            ]
        )
