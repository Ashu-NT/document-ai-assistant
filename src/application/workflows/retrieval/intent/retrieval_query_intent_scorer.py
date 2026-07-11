from src.application.workflows.retrieval.intent.retrieval_query_intent_markers import (
    FIGURE_MARKERS,
    IDENTIFIER_KEYWORD_MARKERS,
    MAINTENANCE_MARKERS,
    OVERVIEW_KEYWORD_MARKERS,
    OVERVIEW_PATTERNS,
    PROCEDURE_MARKERS,
    SAFETY_MARKERS,
    SPECIFICATION_MARKERS,
    TABLE_MARKERS,
    TROUBLESHOOTING_MARKERS,
)
from src.application.workflows.retrieval.intent.retrieval_query_intent_predicates import (
    is_explicit_identifier_lookup,
    looks_like_identifier_listing_query,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.shared.negation_detection import (
    has_non_negated_occurrence as _has_non_negated_occurrence,
)
from src.domain.retrieval import RetrievalQuery

# --- Scored-classifier weights/gates ----------------------------------
#
# Ported from what was previously a first-match-wins if/elif chain (see
# score_candidates()/resolve_scores() below) into the weighted
# multi-signal scoring + minimum-score/minimum-gap gate already proven in
# this codebase for the structurally identical chunk-type classification
# problem (see ChunkSemanticSignalExtractor + ChunkTypeResolver in
# src/application/workflows/parsing/builders/chunking/builders/). Every
# marker/regex list in retrieval_query_intent_markers.py is unchanged from
# the original if/elif version -- only the *decision* logic (first-match-wins
# -> scored-and-gated) changed.
WEIGHT_EXPLICIT = 6  # regex pattern match, or a verb+marker "listing" combo
WEIGHT_KEYWORD = 4  # a single literal substring marker hit
KEYWORD_HIT_CAP = 2  # additional distinct marker hits beyond this don't add more score
MIN_SCORE = 4
MIN_GAP = 2
MAINTENANCE_PROCEDURE_REQUIRED_GAP = 4  # see MAINTENANCE handling below

# Mirrors the original if/elif check order: on an exact score tie, whichever
# intent was checked earlier in that sequence wins (lower rank = higher
# priority). This is the sole tie-break mechanism -- no per-pair override
# table is needed because every exact tie the original code could produce
# is already resolved by preserving its scan order here.
PRIORITY_RANK: dict[RetrievalQueryIntent, int] = {
    RetrievalQueryIntent.FIGURE: 0,
    RetrievalQueryIntent.TABLE: 1,
    RetrievalQueryIntent.IDENTIFIER: 2,
    RetrievalQueryIntent.SPECIFICATION: 3,
    RetrievalQueryIntent.TROUBLESHOOTING: 4,
    RetrievalQueryIntent.SAFETY: 5,
    RetrievalQueryIntent.MAINTENANCE: 6,
    RetrievalQueryIntent.PROCEDURE: 7,
    RetrievalQueryIntent.OVERVIEW: 8,
}

# The original code hard-vetoed MAINTENANCE entirely whenever an explicit
# procedure marker was present (`and not _is_explicit_procedure_query(...)`),
# even if the maintenance signal was overwhelming. Replaced with a "soft
# veto": MAINTENANCE must beat a competing PROCEDURE score by a larger gap
# than usual, rather than being zeroed out unconditionally. This is a
# deliberate, intentional behavior change from the original -- see
# test_maintenance_signal_overwhelms_incidental_procedure_marker.
REQUIRED_GAP_OVERRIDES: dict[tuple[RetrievalQueryIntent, RetrievalQueryIntent], int] = {
    (RetrievalQueryIntent.MAINTENANCE, RetrievalQueryIntent.PROCEDURE): (
        MAINTENANCE_PROCEDURE_REQUIRED_GAP
    ),
}

# Negation handling (negation cue lookback-window check) lives in the shared
# negation_detection module -- scoped to the plain keyword tier only, since
# the explicit regex/combo tier's matches are more structured and a uniform
# "negation nearby" rule doesn't apply as cleanly there. Shared with
# AnswerIntentAnalyzer's own keyword scoring rather than reimplemented.


def _add_keyword_score(
    scores: dict[RetrievalQueryIntent, int],
    intent: RetrievalQueryIntent,
    query_text: str,
    markers: tuple[str, ...],
) -> None:
    hits = sum(
        1 for marker in markers if _has_non_negated_occurrence(query_text, marker)
    )
    if hits <= 0:
        return
    scores[intent] = scores.get(intent, 0) + WEIGHT_KEYWORD * min(hits, KEYWORD_HIT_CAP)


def _add_explicit_score(
    scores: dict[RetrievalQueryIntent, int],
    intent: RetrievalQueryIntent,
    matched: bool,
) -> None:
    if not matched:
        return
    scores[intent] = scores.get(intent, 0) + WEIGHT_EXPLICIT


def score_candidates(
    query_text: str,
    query: RetrievalQuery,
) -> dict[RetrievalQueryIntent, int]:
    scores: dict[RetrievalQueryIntent, int] = {}

    _add_keyword_score(scores, RetrievalQueryIntent.FIGURE, query_text, FIGURE_MARKERS)
    _add_keyword_score(scores, RetrievalQueryIntent.TABLE, query_text, TABLE_MARKERS)

    _add_explicit_score(
        scores,
        RetrievalQueryIntent.IDENTIFIER,
        is_explicit_identifier_lookup(query_text, query)
        or looks_like_identifier_listing_query(query_text),
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.IDENTIFIER, query_text, IDENTIFIER_KEYWORD_MARKERS
    )

    _add_keyword_score(
        scores, RetrievalQueryIntent.SPECIFICATION, query_text, SPECIFICATION_MARKERS
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.TROUBLESHOOTING, query_text, TROUBLESHOOTING_MARKERS
    )
    _add_keyword_score(scores, RetrievalQueryIntent.SAFETY, query_text, SAFETY_MARKERS)
    _add_keyword_score(
        scores, RetrievalQueryIntent.MAINTENANCE, query_text, MAINTENANCE_MARKERS
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.PROCEDURE, query_text, PROCEDURE_MARKERS
    )

    _add_explicit_score(
        scores,
        RetrievalQueryIntent.OVERVIEW,
        any(pattern.search(query_text) for pattern in OVERVIEW_PATTERNS),
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.OVERVIEW, query_text, OVERVIEW_KEYWORD_MARKERS
    )

    return {intent: score for intent, score in scores.items() if score > 0}


def resolve_scores(
    scores: dict[RetrievalQueryIntent, int],
) -> tuple[RetrievalQueryIntent | None, int, RetrievalQueryIntent | None, int]:
    """Picks the winning intent from `scores`, gated by a minimum absolute
    score and a minimum gap over the runner-up (mirroring ChunkTypeResolver).
    Unlike ChunkTypeResolver's single-shot gate-or-GENERAL, this cascades:
    if the top candidate fails its gate, it's demoted and the remaining
    candidates are re-raced, so a gated-off top pick doesn't spuriously
    discard an otherwise-unambiguous runner-up."""
    remaining = sorted(
        scores.items(),
        key=lambda pair: (-pair[1], PRIORITY_RANK.get(pair[0], 99)),
    )
    while remaining:
        top_intent, top_score = remaining[0]
        if top_score < MIN_SCORE:
            return None, 0, None, 0

        runner_up_intent, runner_up_score = (
            remaining[1] if len(remaining) > 1 else (None, 0)
        )

        if runner_up_intent is not None and top_score == runner_up_score:
            return top_intent, top_score, runner_up_intent, runner_up_score

        required_gap = MIN_GAP
        if runner_up_intent is not None:
            required_gap = REQUIRED_GAP_OVERRIDES.get(
                (top_intent, runner_up_intent), MIN_GAP
            )
        if (top_score - runner_up_score) >= required_gap:
            return top_intent, top_score, runner_up_intent, runner_up_score

        remaining = remaining[1:]

    return None, 0, None, 0
