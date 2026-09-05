from __future__ import annotations

import re
from collections.abc import Iterator


class StructuredMarkerMatcher:
    """Matches structured evidence markers against normalized document text.

    Responsibilities:
    - normalize markers and document text consistently;
    - prevent substring false positives such as:
        "fault" matching "default"
        "fit" matching "benefit";
    - support multi-word and punctuated markers such as:
        "possible cause"
        "start/run"
        "pre-commissioning";
    - expose individual matches for higher-level policies such as negation
      handling and evidence scoring.
    """

    def normalize(self, value: str | None) -> str:
        normalized = re.sub(
            r"[\W_]+",
            " ",
            str(value or ""),
            flags=re.UNICODE,
        )
        return " ".join(normalized.strip().lower().split())

    def iter_matches(
        self,
        text: str | None,
        marker: str | None,
    ) -> Iterator[re.Match[str]]:
        normalized_text = self.normalize(text)
        normalized_marker = self.normalize(marker)

        if not normalized_text or not normalized_marker:
            return

        pattern = re.compile(
            rf"(?<!\w){re.escape(normalized_marker)}(?!\w)"
        )

        yield from pattern.finditer(normalized_text)

    def contains(
        self,
        text: str | None,
        marker: str | None,
    ) -> bool:
        return next(
            self.iter_matches(text, marker),
            None,
        ) is not None

    def contains_any(
        self,
        markers: tuple[str, ...],
        *haystacks: str,
    ) -> bool:
        return any(
            self.contains(haystack, marker)
            for marker in markers
            for haystack in haystacks
            if haystack
        )