from __future__ import annotations

from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.intent.answer_intent_decision import (
    AnswerIntentDecision,
    compute_confidence,
)
from src.application.services.answer_generation.intent.answer_intent_ranking import (
    pick_intent,
    runner_up,
)
from src.application.services.answer_generation.intent.answer_intent_vocabulary import (
    ANSWER_INTENT_RULES_VERSION,
    INTENT_PRIORITY,
)
from src.application.services.answer_generation.intent.chunk_content_signal_scorer import (
    apply_chunk_content_signal,
    apply_chunk_type_preference_signal,
)
from src.application.services.answer_generation.intent.question_signal_scorer import (
    apply_maintenance_procedure_disambiguation,
    apply_question_signals,
    apply_retrieval_intent_signal,
    apply_route_signal,
    normalize_text,
)
from src.config.logging import get_logger
from src.domain.common import ChunkType
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

_logger = get_logger(__name__)


class AnswerIntentAnalyzer:
    def analyze(
        self,
        *,
        question: str,
        retrieval_intent: str | None = None,
        chunk_type_preferences: Sequence[ChunkType] | None = None,
        approved_chunks: Sequence[RetrievedChunk] | None = None,
        legacy_query_intent: str | None = None,
        route: str | None = None,
    ) -> AnswerIntentDecision:
        normalized_question = normalize_text(question)
        chunks = list(approved_chunks or [])
        scores = {intent: 0 for intent in INTENT_PRIORITY}
        matched: dict[AnswerIntent, list[str]] = {
            intent: [] for intent in INTENT_PRIORITY
        }

        apply_question_signals(normalized_question, scores, matched)
        apply_route_signal(route, scores, matched)
        apply_retrieval_intent_signal(
            retrieval_intent or legacy_query_intent,
            scores,
            matched,
        )
        apply_chunk_type_preference_signal(
            chunk_type_preferences or [],
            scores,
            matched,
        )
        apply_chunk_content_signal(
            question=normalized_question,
            chunks=chunks,
            scores=scores,
            matched=matched,
        )
        apply_maintenance_procedure_disambiguation(
            normalized_question,
            scores,
            matched,
        )

        best_intent = pick_intent(scores)
        if scores[best_intent] <= 0:
            _logger.info(
                "answer_intent_fallback_general reason=no_strong_signal "
                "rules_version=%s",
                ANSWER_INTENT_RULES_VERSION,
            )
            return AnswerIntentDecision(
                intent=AnswerIntent.GENERAL,
                confidence=0.55,
                reason="No strong answer-format signals were detected.",
                matched_signals=[],
            )

        runner_up_intent, runner_up_score = runner_up(scores, best_intent)
        best_score = scores[best_intent]
        confidence = compute_confidence(
            best_score=best_score,
            runner_up_score=runner_up_score,
        )
        matched_signals = matched[best_intent]
        signal_origin = "question" if any(
            signal.startswith("question:") for signal in matched_signals
        ) else "retrieval/context"
        # margin/runner_up_intent logged unconditionally (not just when
        # contested) so a future report script can aggregate the real
        # margin distribution the same way report_retrieval_intent_fallback_
        # rate.py already aggregates retrieval-intent fallbacks -- collecting
        # this telemetry is the intended prerequisite before ever widening
        # AnswerIntentDecision.is_contested's threshold past an exact tie.
        _logger.info(
            "answer_intent_resolved intent=%s confidence=%s margin=%s "
            "runner_up_intent=%s rules_version=%s",
            best_intent.value,
            confidence,
            best_score - runner_up_score if runner_up_intent is not None else None,
            runner_up_intent.value if runner_up_intent is not None else None,
            ANSWER_INTENT_RULES_VERSION,
        )
        return AnswerIntentDecision(
            intent=best_intent,
            confidence=confidence,
            reason=(
                f"Resolved from {signal_origin} signals with supporting retrieval evidence."
            ),
            matched_signals=matched_signals,
            runner_up_intent=runner_up_intent,
            runner_up_score=runner_up_score,
            best_score=best_score,
        )
