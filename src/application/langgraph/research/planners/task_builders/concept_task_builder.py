from __future__ import annotations

from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.research_text_utils import normalize_theme
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)
from src.application.workflows.shared.identifier_value_pattern import (
    extract_identifier_value,
)


def build_concept_task(
    *,
    plan_builder: ResearchPlanBuilder,
    goal,
    concept: str,
    question: str,
    strategy: RetrievalStrategy,
    answer_intent: str,
    max_results: int,
):
    diagnostics: dict[str, object] = {
        "concept": concept,
        "concept_role": "primary",
        "strategy_hint": strategy.value,
    }
    if strategy == RetrievalStrategy.IDENTIFIER_LOOKUP:
        # `concept` is usually a category label ("part number", "serial
        # number") rather than the actual value, because that's what
        # `keyword_concepts` matches via `CATEGORY_PATTERNS` — the value
        # itself lives elsewhere in the raw request. Comparison-goal
        # concepts (from `split_compare_concepts`) are the exception:
        # there, `concept` often already *is* the value. Try `concept`
        # first so that case still works, then fall back to searching the
        # full request text.
        identifier_value = extract_identifier_value(
            concept
        ) or extract_identifier_value(goal.user_input)
        if identifier_value:
            diagnostics["identifier_value"] = identifier_value
    return plan_builder.build_task(
        title=f"Collect evidence for {concept}",
        question=question,
        strategy_hint=strategy.value,
        answer_intent_hint=answer_intent,
        document_id=goal.document_id,
        expected_evidence_type=normalize_theme(concept),
        max_results=max_results,
        diagnostics=diagnostics,
    )
