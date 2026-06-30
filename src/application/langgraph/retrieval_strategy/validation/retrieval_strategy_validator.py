from __future__ import annotations

import re

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class RetrievalStrategyValidator:
    def validate(
        self,
        decision: RetrievalStrategyDecision,
        *,
        context: RetrievalContext,
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalStrategyDecision:
        issues: list[str] = []
        primary = decision.primary_strategy
        if not isinstance(primary, RetrievalStrategy):
            issues.append("unknown_primary_strategy")
            primary = policy.default_strategy

        confidence = float(decision.confidence or 0.0)
        if confidence < 0.0 or confidence > 1.0:
            issues.append("invalid_confidence")
            confidence = 0.0

        top_k = int(decision.top_k or context.top_k or policy.default_top_k)
        if top_k <= 0 or top_k > policy.max_top_k:
            issues.append("invalid_top_k")
            top_k = min(max(top_k, 1), policy.max_top_k)

        rewritten_query = decision.rewritten_query.strip() if decision.rewritten_query else None
        if rewritten_query == "":
            issues.append("empty_rewritten_query")
            rewritten_query = None
        if rewritten_query and not self._is_related(rewritten_query, context.query_text):
            issues.append("unrelated_rewritten_query")
            rewritten_query = None

        document_id = decision.document_id or context.effective_document_id
        if (
            policy.preserve_document_scope
            and context.effective_document_id is not None
            and document_id != context.effective_document_id
        ):
            issues.append("document_scope_violation")
            document_id = context.effective_document_id

        secondary = [
            strategy
            for strategy in decision.secondary_strategies
            if isinstance(strategy, RetrievalStrategy)
            and strategy != primary
            and strategy != RetrievalStrategy.GENERAL_HYBRID
        ]
        secondary = secondary[: max(policy.max_strategies_per_query - 1, 0)]

        if issues and policy.fallback_to_hybrid:
            return RetrievalStrategyDecision(
                primary_strategy=policy.default_strategy,
                confidence=max(confidence, 0.55),
                reason="Retrieval strategy validation failed, so the selector fell back to GENERAL_HYBRID.",
                signals=decision.signals,
                requires_document=decision.requires_document,
                document_id=document_id,
                query=decision.query or context.query_text,
                rewritten_query=rewritten_query,
                top_k=top_k,
                use_llm_selector=decision.use_llm_selector,
                diagnostics={
                    **dict(decision.diagnostics),
                    "validator_issues": issues,
                    "fallback_used": True,
                },
            )

        return RetrievalStrategyDecision(
            primary_strategy=primary,
            secondary_strategies=secondary,
            confidence=confidence,
            reason=decision.reason,
            signals=decision.signals,
            requires_document=decision.requires_document,
            document_id=document_id,
            query=decision.query or context.query_text,
            rewritten_query=rewritten_query,
            top_k=top_k,
            use_llm_selector=decision.use_llm_selector,
            diagnostics={
                **dict(decision.diagnostics),
                "validator_issues": issues,
            },
        )

    @staticmethod
    def _is_related(rewritten_query: str, original_query: str) -> bool:
        rewritten_tokens = set(_TOKEN_RE.findall(rewritten_query.lower()))
        original_tokens = set(_TOKEN_RE.findall(original_query.lower()))
        if not rewritten_tokens or not original_tokens:
            return True
        overlap = rewritten_tokens.intersection(original_tokens)
        return bool(overlap)
