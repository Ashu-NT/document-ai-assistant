from src.application.workflows.retrieval.intent.retrieval_query_intent_chunk_type_fallback import (
    infer_from_chunk_types,
)
from src.application.workflows.retrieval.intent.retrieval_query_intent_fuzzy_matcher import (
    fuzzy_score_candidates,
)
from src.application.workflows.retrieval.intent.retrieval_query_intent_predicates import (
    is_comparative_query,
    is_document_exploration,
)
from src.application.workflows.retrieval.intent.retrieval_query_intent_scorer import (
    MIN_SCORE,
    WEIGHT_EXPLICIT,
    resolve_scores,
    score_candidates,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_query_intent_classification import (
    RetrievalQueryIntentClassification,
)
from src.config.logging import get_logger
from src.domain.retrieval import RetrievalQuery

_logger = get_logger(__name__)

# Bumped whenever the scoring buckets, weights, gates, or marker lists in the
# intent/ submodules change materially -- logged alongside each resolution so
# a shift in the fallback-rate report
# (scripts/report_retrieval_intent_fallback_rate.py) can be correlated with a
# specific rule-pack version rather than an untracked code change. Mirrors the
# `*_PROMPT_VERSION` convention already used by every LLM-prompt-driven
# classifier in this codebase.
RETRIEVAL_INTENT_RULES_VERSION = "v1"


class RetrievalQueryIntentInferer:
    def resolve(self, query: RetrievalQuery | None) -> RetrievalQueryIntent:
        """Like infer(), but reads RetrievalQuery.detected_intent instead of
        recomputing when the query was already analyzed -- RetrievalQueryAnalyzer
        .analyze() stashes the result there. Callers downstream of analyze()
        within the same request (RetrievalWorkflow, QuestionAnsweringRouter,
        RetrievalContextExpander, DeterministicHybridReranker) should call
        this instead of infer() to avoid re-running the classifier on a query
        whose text hasn't changed since it was analyzed."""
        if (
            query is not None
            and query.analyzed
            and query.detected_intent is not None
        ):
            return RetrievalQueryIntent(query.detected_intent)
        return self.infer(query)

    def infer(self, query: RetrievalQuery | None) -> RetrievalQueryIntent:
        classification = self.classify(query)
        _logger.info(
            "retrieval_intent_resolved intent=%s query_id=%s rules_version=%s",
            classification.intent.value,
            query.query_id if query is not None else None,
            RETRIEVAL_INTENT_RULES_VERSION,
        )
        return classification.intent

    def classify(
        self, query: RetrievalQuery | None
    ) -> RetrievalQueryIntentClassification:
        if query is None:
            _logger.info("retrieval_intent_fallback_general reason=query_is_none")
            return RetrievalQueryIntentClassification(
                intent=RetrievalQueryIntent.GENERAL,
                score=0,
                runner_up_intent=None,
                runner_up_score=0,
                resolution_tier="general",
                fallback_reason="query_is_none",
            )

        query_text = query.effective_query().strip().lower()
        if query_text and is_document_exploration(query_text):
            return RetrievalQueryIntentClassification(
                intent=RetrievalQueryIntent.DOCUMENT_EXPLORATION,
                score=WEIGHT_EXPLICIT,
                runner_up_intent=None,
                runner_up_score=0,
                scores={RetrievalQueryIntent.DOCUMENT_EXPLORATION: WEIGHT_EXPLICIT},
                resolution_tier="scored",
                is_comparative=is_comparative_query(query_text),
            )

        if not query_text:
            chunk_type_intent = infer_from_chunk_types(query)
            if chunk_type_intent is None:
                _logger.info(
                    "retrieval_intent_fallback_general reason=empty_query_text "
                    "query_id=%s",
                    query.query_id,
                )
                return RetrievalQueryIntentClassification(
                    intent=RetrievalQueryIntent.GENERAL,
                    score=0,
                    runner_up_intent=None,
                    runner_up_score=0,
                    resolution_tier="general",
                    fallback_reason="empty_query_text",
                )
            return RetrievalQueryIntentClassification(
                intent=chunk_type_intent,
                score=MIN_SCORE,
                runner_up_intent=None,
                runner_up_score=0,
                resolution_tier="chunk_type_fallback",
            )

        scores = score_candidates(query_text, query)
        winner, score, runner_up, runner_up_score = resolve_scores(scores)
        is_comparative = is_comparative_query(query_text)
        if winner is not None:
            return RetrievalQueryIntentClassification(
                intent=winner,
                score=score,
                runner_up_intent=runner_up,
                runner_up_score=runner_up_score,
                scores=scores,
                resolution_tier="scored",
                is_comparative=is_comparative,
            )

        chunk_type_intent = infer_from_chunk_types(query)
        if chunk_type_intent is not None:
            return RetrievalQueryIntentClassification(
                intent=chunk_type_intent,
                score=MIN_SCORE,
                runner_up_intent=None,
                runner_up_score=0,
                scores=scores,
                resolution_tier="chunk_type_fallback",
                is_comparative=is_comparative,
            )
        if query.has_identifiers():
            return RetrievalQueryIntentClassification(
                intent=RetrievalQueryIntent.IDENTIFIER,
                score=MIN_SCORE,
                runner_up_intent=None,
                runner_up_score=0,
                scores=scores,
                resolution_tier="identifier_fallback",
                is_comparative=is_comparative,
            )

        fuzzy_scores = fuzzy_score_candidates(query_text)
        fuzzy_winner, fuzzy_score, fuzzy_runner_up, fuzzy_runner_up_score = (
            resolve_scores(fuzzy_scores)
        )
        if fuzzy_winner is not None:
            _logger.info(
                "retrieval_intent_fallback_fuzzy intent=%s query_id=%s query_text=%r",
                fuzzy_winner.value,
                query.query_id,
                query_text,
            )
            return RetrievalQueryIntentClassification(
                intent=fuzzy_winner,
                score=fuzzy_score,
                runner_up_intent=fuzzy_runner_up,
                runner_up_score=fuzzy_runner_up_score,
                scores=fuzzy_scores,
                resolution_tier="fuzzy_fallback",
                is_comparative=is_comparative,
            )

        if is_comparative:
            # A comparison shape ("difference between X and Y", "X vs Y")
            # with no topic marker at all still isn't a fully unclassified
            # query -- OVERVIEW's broad, graceful chunk-type preference list
            # (OVERVIEW -> GENERAL -> OPERATION_INSTRUCTION ->
            # INSTALLATION_INSTRUCTION -> TECHNICAL_SPECIFICATION, see
            # RetrievalQueryChunkTypePreferenceMapper) is a materially better
            # default than GENERAL's "no preference at all" fallthrough.
            _logger.info(
                "retrieval_intent_fallback_comparative query_id=%s query_text=%r",
                query.query_id,
                query_text,
            )
            return RetrievalQueryIntentClassification(
                intent=RetrievalQueryIntent.OVERVIEW,
                score=0,
                runner_up_intent=None,
                runner_up_score=0,
                scores=scores,
                resolution_tier="comparative_fallback",
                is_comparative=True,
            )

        _logger.info(
            "retrieval_intent_fallback_general reason=no_pattern_matched "
            "query_id=%s query_text=%r",
            query.query_id,
            query_text,
        )
        return RetrievalQueryIntentClassification(
            intent=RetrievalQueryIntent.GENERAL,
            score=0,
            runner_up_intent=None,
            runner_up_score=0,
            scores=scores,
            resolution_tier="general",
            fallback_reason="no_pattern_matched",
            is_comparative=is_comparative,
        )
