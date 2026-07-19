from typing import Any

from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)
from src.domain.retrieval import RetrievalQuery


def build_decision_trace(
    *,
    analyzed_query: RetrievalQuery,
    generated: GeneratedAnswer,
) -> dict[str, Any]:
    """A single, queryable record of every classification and dispatch
    decision behind one answer -- retrieval intent, answer intent,
    deterministic-dispatch outcome -- under the existing
    `QuestionAnsweringResult.diagnostics` container (PR 7,
    answering_flow_weakness_remediation_plan.md). Deliberately not a new
    top-level `AgentState` field: per the Phase 0 mapping pass, nothing
    downstream needs to route a graph *node* on this information today,
    only read it (reflection reads the nested retrieval result directly;
    dispatch already happened inside AnswerGenerationService by the time
    this is built)."""
    diagnostics = generated.diagnostics or {}
    renderer_used = diagnostics.get("deterministic_renderer")
    return {
        "retrieval_intent": analyzed_query.detected_intent,
        "retrieval_intent_best_score": analyzed_query.intent_best_score,
        "retrieval_intent_runner_up": analyzed_query.intent_runner_up,
        "retrieval_intent_runner_up_score": analyzed_query.intent_runner_up_score,
        "retrieval_intent_gap": analyzed_query.intent_score_gap,
        "answer_intent": (
            generated.answer_intent.value
            if generated.answer_intent is not None
            else None
        ),
        "answer_intent_best_score": diagnostics.get("answer_intent_best_score"),
        "answer_intent_runner_up": diagnostics.get("answer_intent_runner_up"),
        "answer_intent_runner_up_score": diagnostics.get(
            "answer_intent_runner_up_score"
        ),
        "answer_intent_margin": diagnostics.get("answer_intent_margin"),
        "deterministic_bypassed": diagnostics.get("deterministic_dispatch_bypassed"),
        "bypass_reason": diagnostics.get("deterministic_dispatch_bypass_reason"),
        # `renderer_used` (not `deterministic_dispatch_bypassed`) is the
        # authoritative signal for which path actually executed --
        # AnswerGenerationService can decide not to bypass and *still* fall
        # through to the LLM if the dispatcher finds no matching renderer
        # for the resolved intent (see AnswerGenerationService.generate()).
        "renderer_used": renderer_used,
        "llm_used": renderer_used is None,
    }
