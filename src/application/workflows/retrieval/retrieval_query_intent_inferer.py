import re

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_query_intent_classification import (
    RetrievalQueryIntentClassification,
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

# Deterministic, lightweight negation handling: a keyword marker match is
# ignored if a negation cue appears shortly before it (e.g. "not related to
# safety" no longer contributes a SAFETY hit). Scoped to the plain keyword
# tier only -- the explicit regex/combo tier's matches are more structured
# and a uniform "negation nearby" rule doesn't apply as cleanly there.
_NEGATION_CUES: tuple[str, ...] = (
    "not",
    "excluding",
    "without",
    "unrelated to",
    "aside from",
    "except",
)
_NEGATION_LOOKBACK_TOKENS = 4


def _is_negated(query_text: str, marker_start: int) -> bool:
    preceding_tokens = query_text[:marker_start].split()[-_NEGATION_LOOKBACK_TOKENS:]
    preceding_text = " ".join(preceding_tokens)
    return any(cue in preceding_text for cue in _NEGATION_CUES)


def _has_non_negated_occurrence(query_text: str, marker: str) -> bool:
    search_from = 0
    while True:
        index = query_text.find(marker, search_from)
        if index == -1:
            return False
        if not _is_negated(query_text, index):
            return True
        search_from = index + 1


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
