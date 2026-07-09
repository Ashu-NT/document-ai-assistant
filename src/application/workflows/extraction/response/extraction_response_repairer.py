from __future__ import annotations

import re


class ExtractionResponseRepairer:
    """Deterministically repairs a narrow class of malformed JSON responses.

    This is intentionally conservative:
    - only JSON objects are considered repairable
    - only trailing-comma cleanup, balanced-root slicing, and missing closing
      bracket/brace repair are attempted
    - responses truncated mid-string or mid-key/value separator still fail
    """

    _TRAILING_COMMA_PATTERN = re.compile(r",(\s*[}\]])")

    def repair(self, payload: str) -> str | None:
        candidate = (payload or "").strip()
        if not candidate or not candidate.startswith("{"):
            return None

        if candidate.rstrip().endswith(":"):
            return None

        structural_state = self._scan(candidate)
        if structural_state is None:
            return None

        balanced_root_end, stack, in_string = structural_state
        if in_string:
            return None

        if balanced_root_end is not None:
            trailing = candidate[balanced_root_end + 1 :].strip()
            if trailing:
                candidate = candidate[: balanced_root_end + 1]
                stack = []

        candidate = self._remove_trailing_commas(candidate)
        if candidate.rstrip().endswith(":"):
            return None

        if stack:
            candidate = candidate + "".join(
                "}" if opener == "{" else "]" for opener in reversed(stack)
            )
            candidate = self._remove_trailing_commas(candidate)

        return candidate

    def _scan(self, payload: str) -> tuple[int | None, list[str], bool] | None:
        stack: list[str] = []
        in_string = False
        escape = False
        balanced_root_end: int | None = None

        for index, character in enumerate(payload):
            if in_string:
                if escape:
                    escape = False
                    continue
                if character == "\\":
                    escape = True
                    continue
                if character == '"':
                    in_string = False
                continue

            if character == '"':
                in_string = True
                continue

            if character in "{[":
                stack.append(character)
                continue

            if character not in "}]":
                continue

            if not stack:
                return None

            opener = stack.pop()
            if (opener, character) not in {("{", "}"), ("[", "]")}:
                return None

            if not stack:
                balanced_root_end = index

        return balanced_root_end, stack, in_string

    @classmethod
    def _remove_trailing_commas(cls, payload: str) -> str:
        previous = payload
        while True:
            updated = cls._TRAILING_COMMA_PATTERN.sub(r"\1", previous)
            if updated == previous:
                return updated
            previous = updated
