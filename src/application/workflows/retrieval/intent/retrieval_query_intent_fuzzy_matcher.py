import difflib
import re

from src.application.workflows.retrieval.intent.retrieval_query_intent_markers import (
    FIGURE_MARKERS,
    MAINTENANCE_MARKERS,
    OVERVIEW_KEYWORD_MARKERS,
    PROCEDURE_MARKERS,
    SAFETY_MARKERS,
    SPECIFICATION_MARKERS,
    TABLE_MARKERS,
    TROUBLESHOOTING_MARKERS,
)
from src.application.workflows.retrieval.intent.retrieval_query_intent_scorer import (
    KEYWORD_HIT_CAP,
    WEIGHT_KEYWORD,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.shared.negation_detection import (
    is_negated as _is_negated,
)

# --- Typo-tolerant fuzzy fallback ---------------------------------------
#
# Only ever consulted when the exact/keyword scoring pass above matched
# NOTHING at all (a single exact hit already clears MIN_SCORE and wins, so
# "no winner" implies "zero markers matched") -- a misspelled marker like
# "troublshoot" or "presure" would otherwise fall straight to GENERAL. Single
# words only (multi-word markers like "service interval" aren't meaningful
# fuzzy-match targets for one query token) and a floor on marker/token length,
# since short words produce unreliable edit-distance ratios (e.g. "step" vs
# "stop"). Cutoff tuned empirically against real typo examples (0.833-0.957)
# with a safety margin above realistic negative-control words (<=0.8).
_FUZZY_MATCH_CUTOFF = 0.82
_FUZZY_MIN_WORD_LENGTH = 5

_FUZZY_MARKER_LOOKUP: dict[str, RetrievalQueryIntent] = {
    marker: intent
    for intent, markers in (
        (RetrievalQueryIntent.FIGURE, FIGURE_MARKERS),
        (RetrievalQueryIntent.TABLE, TABLE_MARKERS),
        (RetrievalQueryIntent.SPECIFICATION, SPECIFICATION_MARKERS),
        (RetrievalQueryIntent.TROUBLESHOOTING, TROUBLESHOOTING_MARKERS),
        (RetrievalQueryIntent.SAFETY, SAFETY_MARKERS),
        (RetrievalQueryIntent.MAINTENANCE, MAINTENANCE_MARKERS),
        (RetrievalQueryIntent.PROCEDURE, PROCEDURE_MARKERS),
        (RetrievalQueryIntent.OVERVIEW, OVERVIEW_KEYWORD_MARKERS),
    )
    for marker in markers
    if " " not in marker and len(marker) >= _FUZZY_MIN_WORD_LENGTH
}
_FUZZY_MARKER_POOL: tuple[str, ...] = tuple(_FUZZY_MARKER_LOOKUP.keys())


def fuzzy_score_candidates(query_text: str) -> dict[RetrievalQueryIntent, int]:
    # Position-aware (not a deduped token set) so a negated occurrence of a
    # word that also happens to BE a marker verbatim -- e.g. "safety" in
    # "not a safety concern" -- doesn't get resurrected here after the exact
    # keyword pass above correctly suppressed it. A fuzzy "match" of a token
    # against itself is a ratio of 1.0, so without this check negation would
    # be silently bypassed for any word that is itself an exact marker.
    hit_counts: dict[RetrievalQueryIntent, int] = {}
    for match in re.finditer(r"[a-z]+", query_text):
        token = match.group()
        if len(token) < _FUZZY_MIN_WORD_LENGTH:
            continue
        close_matches = difflib.get_close_matches(
            token, _FUZZY_MARKER_POOL, n=1, cutoff=_FUZZY_MATCH_CUTOFF
        )
        if not close_matches or _is_negated(query_text, match.start()):
            continue
        intent = _FUZZY_MARKER_LOOKUP[close_matches[0]]
        hit_counts[intent] = hit_counts.get(intent, 0) + 1

    return {
        intent: WEIGHT_KEYWORD * min(count, KEYWORD_HIT_CAP)
        for intent, count in hit_counts.items()
    }
