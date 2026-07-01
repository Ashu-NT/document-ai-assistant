from __future__ import annotations

from src.application.langgraph.strategy_advisor.advisor_models import StrategyAdvisorProposal


class StrategyReasonBuilder:
    def build_merge_reason(
        self,
        *,
        query_text: str,
        deterministic_reason: str,
        proposal: StrategyAdvisorProposal,
        merged_strategy_names: list[str],
    ) -> str:
        concept_text = ", ".join(proposal.concepts) or "the detected request concepts"
        strategy_text = ", ".join(merged_strategy_names) or "GENERAL_HYBRID"
        if deterministic_reason:
            return (
                f"{deterministic_reason} The guarded advisor preserved the deterministic "
                f"selection and added support for {concept_text}, so the final retrieval "
                f"plan uses {strategy_text} for: {query_text.strip()}."
            )
        return (
            f"The guarded advisor preserved the deterministic selection and added support "
            f"for {concept_text}, so the final retrieval plan uses {strategy_text} "
            f"for: {query_text.strip()}."
        )

