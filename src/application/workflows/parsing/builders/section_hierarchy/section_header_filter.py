import re

from src.application.workflows.parsing.canonical_element import CanonicalElement

_BRANDING_HEADERS = {
    "environmentally",
    "responsible solutions",
    "engineered",
    "environmentally responsible solutions engineered",
}
_SENTENCE_START_MARKERS = {
    "after",
    "before",
    "ensure",
    "if",
    "once",
    "that",
    "the",
    "these",
    "this",
    "when",
    "while",
}
_NUMBERED_HEADER_RE = re.compile(
    r"^(?:chapter|section|part)?\s*\d+(?:\.\d+)*(?:[.)])?\b",
    re.IGNORECASE,
)
_TASK_HEADER_RE = re.compile(
    r"^(?:(?:prep|lab)\s+task|task|step|procedure|installation|operation|maintenance|troubleshooting|commissioning|shutdown)\b",
    re.IGNORECASE,
)


class SectionHeaderFilter:
    def filter(
        self,
        headers: list[CanonicalElement],
    ) -> list[CanonicalElement]:
        return [header for header in headers if self._is_viable_header(header)]

    def _is_viable_header(
        self,
        header: CanonicalElement,
    ) -> bool:
        text = (header.text or "").strip()
        if not text:
            return False

        normalized = self._normalize(text)
        if not normalized:
            return False
        if normalized in _BRANDING_HEADERS:
            return False
        if self._looks_like_sentence(normalized, text):
            return False
        return True

    @staticmethod
    def _looks_like_sentence(
        normalized: str,
        raw_text: str,
    ) -> bool:
        if _NUMBERED_HEADER_RE.match(normalized):
            return False
        if _TASK_HEADER_RE.match(normalized):
            return False

        words = normalized.split()
        if len(words) < 6:
            return False

        if raw_text.rstrip().endswith((".", "!", "?", ";")):
            return True

        if words[0] in _SENTENCE_START_MARKERS and len(words) >= 7:
            return True

        raw_words = [word for word in raw_text.split() if word]
        if len(raw_words) < 6:
            return False

        title_like_words = sum(
            1
            for word in raw_words
            if word[:1].isdigit() or word.isupper() or word[:1].isupper()
        )
        title_like_ratio = title_like_words / len(raw_words)
        return len(raw_words) >= 9 and title_like_ratio < 0.45

    @staticmethod
    def _normalize(value: str | None) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().lower())
