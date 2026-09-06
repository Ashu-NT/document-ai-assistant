import re
from collections import Counter

from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


_CALLOUT_LABEL_PATTERN = re.compile(
    r"^(?:warning|caution|danger|notice|note|important)(?:\s*[:!])?$",
    re.IGNORECASE,
)
_TABLE_ROLE_LABELS = frozenset(
    {
        "cause",
        "corrective action",
        "description",
        "fault",
        "possible cause",
        "remedy",
        "result",
        "symptom",
        "value",
    }
)


class LocalSemanticHeaderDetector:
    """Finds Docling headers that describe local evidence, not outline nodes."""

    def detect(
        self,
        headers: list[ParsedCanonicalElement],
    ) -> set[str]:
        normalized_by_id = {
            header.element_id: self._normalize(header.text)
            for header in headers
        }
        counts = Counter(normalized_by_id.values())
        local_ids: set[str] = set()

        for index, header in enumerate(headers):
            normalized = normalized_by_id[header.element_id]
            if not normalized:
                continue
            if _CALLOUT_LABEL_PATTERN.fullmatch(normalized):
                local_ids.add(header.element_id)
                continue
            if normalized in _TABLE_ROLE_LABELS and counts[normalized] > 1:
                local_ids.add(header.element_id)
                continue
            if self._is_repeated_alert_description(header, normalized, counts):
                local_ids.add(header.element_id)
                continue
            if self._follows_callout(headers, index, normalized_by_id):
                local_ids.add(header.element_id)

        return local_ids

    @staticmethod
    def _is_repeated_alert_description(
        header: ParsedCanonicalElement,
        normalized: str,
        counts: Counter[str],
    ) -> bool:
        text = (header.text or "").strip()
        return text.endswith("!") and counts[normalized] > 1

    @staticmethod
    def _follows_callout(
        headers: list[ParsedCanonicalElement],
        index: int,
        normalized_by_id: dict[str, str],
    ) -> bool:
        if index == 0:
            return False
        current = headers[index]
        previous = headers[index - 1]
        if (current.page_start or current.page_end) != (
            previous.page_start or previous.page_end
        ):
            return False
        previous_text = normalized_by_id[previous.element_id]
        current_text = (current.text or "").strip()
        return bool(
            _CALLOUT_LABEL_PATTERN.fullmatch(previous_text)
            and current_text.endswith(("!", ":"))
        )

    @staticmethod
    def _normalize(value: str | None) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().casefold())
