import difflib
import re

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_query_intent_classification import (
    RetrievalQueryIntentClassification,
)
from src.application.workflows.shared.negation_detection import (
    has_non_negated_occurrence as _has_non_negated_occurrence,
    is_negated as _is_negated,
)
from src.config.logging import get_logger
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery

_logger = get_logger(__name__)

# Bumped whenever the scoring buckets, weights, gates, or marker lists below
# change materially -- logged alongside each resolution so a shift in the
# fallback-rate report (scripts/report_retrieval_intent_fallback_rate.py) can
# be correlated with a specific rule-pack version rather than an untracked
# code change. Mirrors the `*_PROMPT_VERSION` convention already used by
# every LLM-prompt-driven classifier in this codebase.
RETRIEVAL_INTENT_RULES_VERSION = "v1"

# Patterns that signal the user is asking about what a document contains or how
# it is structured, rather than asking for a specific fact inside the document.
#
# Each pattern covers a semantic shape rather than a literal phrase so that
# novel phrasings still match without a growing hardcoded list.
_EXPLORATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    # "what (information|content|data) is/are in/inside/within this/the ..."
    re.compile(
        r"what\s+(information|content|data|details?)\s+(is|are)\s+(in|inside|within|available\s+in)\b"
    ),
    # "what does this/the document/manual/pdf/file contain/cover/include/have"
    re.compile(
        r"what\s+does\s+(this|the)\s+\S+\s+(contain|cover|include|have|describe|document)\b"
    ),
    # "what sections/chapters/topics/identifiers/tables/figures/... are/exist/available/covered"
    re.compile(
        r"what\s+(sections?|chapters?|topics?|subjects?|parts?|identifiers?|part\s+numbers?|"
        r"serial\s+numbers?|model\s+numbers?|tables?|figures?|images?|pictures?|assets?|"
        r"equipment|components?|products?|devices?|systems?)\s+"
        r"(are|is|exist|available|present|covered|listed|documented|mentioned|referenced|in\s+(this|the))\b"
    ),
    # "what is documented/available/covered/described here or in this"
    re.compile(
        r"what\s+is\s+(documented|available|covered|described|listed|included)\s+"
        r"(here|in\s+this|in\s+the)\b"
    ),
    # "what is in this document/pdf/manual/file/report"
    re.compile(
        r"what\s+is\s+in\s+(this|the)\s+(document|pdf|manual|file|report|guide|datasheet|drawing)\b"
    ),
    # "what can I find in this"
    re.compile(r"what\s+(can|could)\s+\w+\s+find\s+(in|inside|within)\b"),
    # "list / show / enumerate / display sections / structure / identifiers / tables / ..."
    re.compile(
        r"(list|show|display|enumerate|give\s+me|provide)\s+(all\s+|the\s+)?"
        r"(sections?|chapters?|topics?|structure|contents?|identifiers?|tables?|figures?|assets?|equipment)\b"
    ),
    # "document / manual / pdf structure / outline / overview / contents / index"
    re.compile(
        r"(document|manual|pdf|file|report)\s+"
        r"(structure|outline|overview|contents?|index|inventory|coverage)\b"
    ),
    # "what topics/subjects/areas are covered/discussed/addressed in"
    re.compile(
        r"what\s+(topics?|subjects?|areas?|items?|things?)\s+(are|is)\s+"
        r"(covered|discussed|addressed|documented|included)\b"
    ),
    # "what is this document/manual/pdf about"
    re.compile(
        r"what\s+is\s+(this|the)\s+(document|manual|pdf|file|report|guide|datasheet)\s+about\b"
    ),
)
_EXPLICIT_IDENTIFIER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(serial|part|order|model|drawing|certificate|approval|position|tag)\s+"
        r"(number|numbers|no|code|codes|designation)\b"
    ),
    re.compile(r"\bspare\s+part\s+(number|no|code)\b"),
    re.compile(r"\bordering\s+code\b"),
    re.compile(r"\border\s+code\b"),
    re.compile(r"\bwhat\s+product\s+is\s+type\s+[a-z0-9-]+\b"),
    re.compile(r"\bwhat\s+is\s+type\s+[a-z0-9-]+\b"),
    re.compile(r"\bwhat\s+is\s+position\s+[a-z0-9-]+\b"),
)
_IDENTIFIER_LISTING_VERBS: tuple[str, ...] = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)
_IDENTIFIER_LISTING_MARKERS: tuple[str, ...] = (
    "serial",
    "part",
    "order code",
    "order number",
    "model",
    "drawing",
    "certificate",
    "tag",
    "manufacturer",
    "supplier",
)
_OVERVIEW_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bwhat\s+does\s+.+\s+do\b"),
    re.compile(r"\bwhat\s+is\s+.+\s+used\s+for\b"),
    re.compile(r"\bwhat\s+is\s+the\s+(purpose|function)\s+of\b"),
    re.compile(r"\bhow\s+does\s+.+\s+work\b"),
)
_PROCEDURE_MARKERS: tuple[str, ...] = (
    "how to",
    "procedure",
    "steps",
    "step",
    "replace",
    "install",
    "configure",
    "calibrate",
    "start",
    "run",
    "restart",
    "remove",
    "connect",
    "shutdown",
    "commission",
    "commissioning",
    "lubricate",
)
# NOTE on cross-module duplication (investigated, not merged): "general
# maintenance topic" detection is independently reimplemented in at least
# three places -- here, AnswerIntentAnalyzer._MAINTENANCE_TERMS (answer
# formatting), and RetrievalSignalExtractor._MAINTENANCE_TERMS (LangGraph
# strategy signals) -- and their vocabularies have drifted by more than a
# marker or two (e.g. this list deliberately excludes bare "service" and
# "inspection", which the other two include, since those bare words are
# broad enough to misfire on retrieval chunk-type targeting specifically --
# "inspection" alone already overlaps AnswerIntentAnalyzer's OWN
# CERTIFICATION_TERMS). This is unlike the MAINTENANCE_INTERVAL_MARKERS
# consolidation in maintenance_signal_detection.py, where the two lists
# solved the identical narrow sub-problem for two consumers and differed by
# exactly one marker each way -- a safe, mechanical merge. Here the three
# lists serve three different downstream decisions (what to retrieve vs. how
# to format an answer vs. which strategy signal to weight) with different
# false-positive tolerances, so forcing a shared vocabulary would either
# broaden retrieval's targeting (risking wrong chunk types) or narrow answer
# formatting's tuning. Left separate, deliberately, rather than merged.
_MAINTENANCE_MARKERS: tuple[str, ...] = (
    "maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "maintenance interval",
    "maintenance intervals",
    "maintenance task",
    "maintenance tasks",
    "preventive maintenance",
    "oil change",
    "lubricat",
    "grease",
    "how often",
    "interval",
)
_FIGURE_MARKERS: tuple[str, ...] = ("figure", "diagram", "drawing", "schematic", "image")
_TABLE_MARKERS: tuple[str, ...] = (
    "table",
    "spare part",
    "parts list",
    "spare parts list",
    "matrix",
)
_IDENTIFIER_KEYWORD_MARKERS: tuple[str, ...] = (
    "serial number",
    "part number",
    "part no",
    "order code",
    "order number",
    "model number",
    "drawing number",
    "certificate number",
    "what is position ",
)
_SPECIFICATION_MARKERS: tuple[str, ...] = (
    "specification",
    "specifications",
    "parameter",
    "voltage",
    "current",
    "tolerance",
    "dimension",
    "torque",
    "pressure",
    "approval",
    "certificate",
)
_TROUBLESHOOTING_MARKERS: tuple[str, ...] = (
    "troubleshoot",
    "problem",
    "fault",
    "error",
    "not working",
    "causes",
    "remedies",
    "diagnose",
    "symptom",
)
_SAFETY_MARKERS: tuple[str, ...] = ("safety", "warning", "danger", "hazard")
_OVERVIEW_KEYWORD_MARKERS: tuple[str, ...] = (
    "overview",
    "summary",
    "introduction",
    "explain",
    "objective",
    "purpose",
    "function",
)
_COMPARATIVE_MARKERS: tuple[str, ...] = (
    "difference between",
    "compare",
    "comparison",
    " vs ",
    " vs. ",
    " versus ",
)

# --- Scored-classifier weights/gates ----------------------------------
#
# Ported from what was previously a first-match-wins if/elif chain (see
# _score_candidates()/_resolve_scores() below) into the weighted
# multi-signal scoring + minimum-score/minimum-gap gate already proven in
# this codebase for the structurally identical chunk-type classification
# problem (see ChunkSemanticSignalExtractor + ChunkTypeResolver in
# src/application/workflows/parsing/builders/chunking/builders/). Every
# marker/regex list above is unchanged from the original if/elif version --
# only the *decision* logic (first-match-wins -> scored-and-gated) changed.
_WEIGHT_EXPLICIT = 6  # regex pattern match, or a verb+marker "listing" combo
_WEIGHT_KEYWORD = 4  # a single literal substring marker hit
_KEYWORD_HIT_CAP = 2  # additional distinct marker hits beyond this don't add more score
_MIN_SCORE = 4
_MIN_GAP = 2
_MAINTENANCE_PROCEDURE_REQUIRED_GAP = 4  # see MAINTENANCE handling below

# Mirrors the original if/elif check order: on an exact score tie, whichever
# intent was checked earlier in that sequence wins (lower rank = higher
# priority). This is the sole tie-break mechanism -- no per-pair override
# table is needed because every exact tie the original code could produce
# is already resolved by preserving its scan order here.
_PRIORITY_RANK: dict[RetrievalQueryIntent, int] = {
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
_REQUIRED_GAP_OVERRIDES: dict[tuple[RetrievalQueryIntent, RetrievalQueryIntent], int] = {
    (RetrievalQueryIntent.MAINTENANCE, RetrievalQueryIntent.PROCEDURE): (
        _MAINTENANCE_PROCEDURE_REQUIRED_GAP
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
    scores[intent] = scores.get(intent, 0) + _WEIGHT_KEYWORD * min(hits, _KEYWORD_HIT_CAP)


def _add_explicit_score(
    scores: dict[RetrievalQueryIntent, int],
    intent: RetrievalQueryIntent,
    matched: bool,
) -> None:
    if not matched:
        return
    scores[intent] = scores.get(intent, 0) + _WEIGHT_EXPLICIT


def _score_candidates(
    query_text: str,
    query: RetrievalQuery,
) -> dict[RetrievalQueryIntent, int]:
    scores: dict[RetrievalQueryIntent, int] = {}

    _add_keyword_score(scores, RetrievalQueryIntent.FIGURE, query_text, _FIGURE_MARKERS)
    _add_keyword_score(scores, RetrievalQueryIntent.TABLE, query_text, _TABLE_MARKERS)

    _add_explicit_score(
        scores,
        RetrievalQueryIntent.IDENTIFIER,
        _is_explicit_identifier_lookup(query_text, query)
        or _looks_like_identifier_listing_query(query_text),
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.IDENTIFIER, query_text, _IDENTIFIER_KEYWORD_MARKERS
    )

    _add_keyword_score(
        scores, RetrievalQueryIntent.SPECIFICATION, query_text, _SPECIFICATION_MARKERS
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.TROUBLESHOOTING, query_text, _TROUBLESHOOTING_MARKERS
    )
    _add_keyword_score(scores, RetrievalQueryIntent.SAFETY, query_text, _SAFETY_MARKERS)
    _add_keyword_score(
        scores, RetrievalQueryIntent.MAINTENANCE, query_text, _MAINTENANCE_MARKERS
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.PROCEDURE, query_text, _PROCEDURE_MARKERS
    )

    _add_explicit_score(
        scores,
        RetrievalQueryIntent.OVERVIEW,
        any(pattern.search(query_text) for pattern in _OVERVIEW_PATTERNS),
    )
    _add_keyword_score(
        scores, RetrievalQueryIntent.OVERVIEW, query_text, _OVERVIEW_KEYWORD_MARKERS
    )

    return {intent: score for intent, score in scores.items() if score > 0}


def _resolve_scores(
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
        key=lambda pair: (-pair[1], _PRIORITY_RANK.get(pair[0], 99)),
    )
    while remaining:
        top_intent, top_score = remaining[0]
        if top_score < _MIN_SCORE:
            return None, 0, None, 0

        runner_up_intent, runner_up_score = (
            remaining[1] if len(remaining) > 1 else (None, 0)
        )

        if runner_up_intent is not None and top_score == runner_up_score:
            return top_intent, top_score, runner_up_intent, runner_up_score

        required_gap = _MIN_GAP
        if runner_up_intent is not None:
            required_gap = _REQUIRED_GAP_OVERRIDES.get(
                (top_intent, runner_up_intent), _MIN_GAP
            )
        if (top_score - runner_up_score) >= required_gap:
            return top_intent, top_score, runner_up_intent, runner_up_score

        remaining = remaining[1:]

    return None, 0, None, 0


def _is_document_exploration(query_text: str) -> bool:
    for pattern in _EXPLORATION_PATTERNS:
        if pattern.search(query_text):
            return True
    return False


def _is_explicit_identifier_lookup(
    query_text: str,
    query: RetrievalQuery | None,
) -> bool:
    if any(pattern.search(query_text) for pattern in _EXPLICIT_IDENTIFIER_PATTERNS):
        return True

    if query is None or not query.has_identifiers():
        return False

    if any(
        marker in query_text
        for marker in (
            " mean",
            " means",
            "meaning",
            "stand for",
            "stands for",
            "designation",
            "position ",
            "type ",
        )
    ):
        return True

    return bool(
        re.search(r"\bwhat\s+does\s+[a-z0-9-]+\s+mean\b", query_text)
        or re.search(r"\bwhat\s+is\s+position\s+[a-z0-9-]+\b", query_text)
    )


def _contains_identifier_reference(query_text: str) -> bool:
    return any(marker in query_text for marker in _IDENTIFIER_LISTING_MARKERS)


def _looks_like_identifier_listing_query(query_text: str) -> bool:
    if not any(marker in query_text for marker in _IDENTIFIER_LISTING_VERBS):
        return False
    return _contains_identifier_reference(query_text)


def _is_comparative_query(query_text: str) -> bool:
    return any(marker in query_text for marker in _COMPARATIVE_MARKERS)


# --- Typo-tolerant fuzzy fallback ---------------------------------------
#
# Only ever consulted when the exact/keyword scoring pass above matched
# NOTHING at all (a single exact hit already clears _MIN_SCORE and wins, so
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
        (RetrievalQueryIntent.FIGURE, _FIGURE_MARKERS),
        (RetrievalQueryIntent.TABLE, _TABLE_MARKERS),
        (RetrievalQueryIntent.SPECIFICATION, _SPECIFICATION_MARKERS),
        (RetrievalQueryIntent.TROUBLESHOOTING, _TROUBLESHOOTING_MARKERS),
        (RetrievalQueryIntent.SAFETY, _SAFETY_MARKERS),
        (RetrievalQueryIntent.MAINTENANCE, _MAINTENANCE_MARKERS),
        (RetrievalQueryIntent.PROCEDURE, _PROCEDURE_MARKERS),
        (RetrievalQueryIntent.OVERVIEW, _OVERVIEW_KEYWORD_MARKERS),
    )
    for marker in markers
    if " " not in marker and len(marker) >= _FUZZY_MIN_WORD_LENGTH
}
_FUZZY_MARKER_POOL: tuple[str, ...] = tuple(_FUZZY_MARKER_LOOKUP.keys())


def _fuzzy_score_candidates(query_text: str) -> dict[RetrievalQueryIntent, int]:
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
        intent: _WEIGHT_KEYWORD * min(count, _KEYWORD_HIT_CAP)
        for intent, count in hit_counts.items()
    }


def _infer_from_chunk_types(query: RetrievalQuery) -> RetrievalQueryIntent | None:
    if ChunkType.SPARE_PARTS_TABLE in query.chunk_types:
        return RetrievalQueryIntent.TABLE
    if ChunkType.DRAWING_REFERENCE in query.chunk_types:
        return RetrievalQueryIntent.FIGURE
    if ChunkType.SAFETY_WARNING in query.chunk_types:
        return RetrievalQueryIntent.SAFETY
    if ChunkType.TROUBLESHOOTING in query.chunk_types:
        return RetrievalQueryIntent.TROUBLESHOOTING
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.MAINTENANCE_INTERVAL,
            ChunkType.MAINTENANCE_PROCEDURE,
        }
    ):
        return RetrievalQueryIntent.MAINTENANCE
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.INSTALLATION_INSTRUCTION,
            ChunkType.OPERATION_INSTRUCTION,
        }
    ):
        return RetrievalQueryIntent.PROCEDURE
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.TECHNICAL_SPECIFICATION,
            ChunkType.CERTIFICATION_INFO,
        }
    ):
        return RetrievalQueryIntent.SPECIFICATION
    return None


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
        if query_text and _is_document_exploration(query_text):
            return RetrievalQueryIntentClassification(
                intent=RetrievalQueryIntent.DOCUMENT_EXPLORATION,
                score=_WEIGHT_EXPLICIT,
                runner_up_intent=None,
                runner_up_score=0,
                scores={RetrievalQueryIntent.DOCUMENT_EXPLORATION: _WEIGHT_EXPLICIT},
                resolution_tier="scored",
                is_comparative=_is_comparative_query(query_text),
            )

        if not query_text:
            chunk_type_intent = _infer_from_chunk_types(query)
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
                score=_MIN_SCORE,
                runner_up_intent=None,
                runner_up_score=0,
                resolution_tier="chunk_type_fallback",
            )

        scores = _score_candidates(query_text, query)
        winner, score, runner_up, runner_up_score = _resolve_scores(scores)
        is_comparative = _is_comparative_query(query_text)
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

        chunk_type_intent = _infer_from_chunk_types(query)
        if chunk_type_intent is not None:
            return RetrievalQueryIntentClassification(
                intent=chunk_type_intent,
                score=_MIN_SCORE,
                runner_up_intent=None,
                runner_up_score=0,
                scores=scores,
                resolution_tier="chunk_type_fallback",
                is_comparative=is_comparative,
            )
        if query.has_identifiers():
            return RetrievalQueryIntentClassification(
                intent=RetrievalQueryIntent.IDENTIFIER,
                score=_MIN_SCORE,
                runner_up_intent=None,
                runner_up_score=0,
                scores=scores,
                resolution_tier="identifier_fallback",
                is_comparative=is_comparative,
            )

        fuzzy_scores = _fuzzy_score_candidates(query_text)
        fuzzy_winner, fuzzy_score, fuzzy_runner_up, fuzzy_runner_up_score = (
            _resolve_scores(fuzzy_scores)
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
