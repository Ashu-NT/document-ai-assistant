from __future__ import annotations

# Deterministic, lightweight negation handling: a keyword marker match is
# ignored if a negation cue appears shortly before it (e.g. "not related to
# safety" no longer contributes a SAFETY hit). Extracted from
# RetrievalQueryIntentInferer so AnswerIntentAnalyzer's own keyword scoring
# can share the identical negation-cue vocabulary and lookback-window logic
# instead of re-implementing it.
NEGATION_CUES: tuple[str, ...] = (
    "not",
    "excluding",
    "without",
    "unrelated to",
    "aside from",
    "except",
)
NEGATION_LOOKBACK_TOKENS = 4


def is_negated(text: str, marker_start: int) -> bool:
    preceding_tokens = text[:marker_start].split()[-NEGATION_LOOKBACK_TOKENS:]
    preceding_text = " ".join(preceding_tokens)
    return any(cue in preceding_text for cue in NEGATION_CUES)


def has_non_negated_occurrence(text: str, marker: str) -> bool:
    search_from = 0
    while True:
        index = text.find(marker, search_from)
        if index == -1:
            return False
        if not is_negated(text, index):
            return True
        search_from = index + 1
