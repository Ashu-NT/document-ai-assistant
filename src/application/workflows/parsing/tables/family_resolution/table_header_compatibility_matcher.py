from __future__ import annotations

from src.application.workflows.parsing.tables.structure.table_header_text_normalizer import (
    normalize_table_header_text,
)
from src.application.workflows.parsing.tables.table_header_signature_builder import (
    TableHeaderSignatureBuilder,
)
from src.domain.assets import TableAsset


class TableHeaderCompatibilityMatcher:
    def __init__(
        self,
        *,
        header_signature_builder: TableHeaderSignatureBuilder | None = None,
    ) -> None:
        self.header_signature_builder = (
            header_signature_builder or TableHeaderSignatureBuilder()
        )

    def are_compatible(
        self,
        previous_table: TableAsset,
        current_table: TableAsset,
    ) -> bool:
        previous_signature = self.header_signature_builder.build(previous_table)
        current_signature = self.header_signature_builder.build(current_table)
        if previous_signature and previous_signature == current_signature:
            return True

        previous_header_text = self._header_text(previous_table)
        current_header_text = self._header_text(current_table)
        if not previous_header_text or not current_header_text:
            return False
        if previous_header_text == current_header_text:
            return True

        if self._tokens_overlap_enough(previous_header_text, current_header_text):
            return True

        return self._compatible_after_stripping_umbrella(previous_table, current_table)

    def _header_text(self, table: TableAsset) -> str | None:
        return self._joined_path_text(self.header_signature_builder.build_paths(table))

    def _compatible_after_stripping_umbrella(
        self,
        previous_table: TableAsset,
        current_table: TableAsset,
    ) -> bool:
        """Continuation pages sometimes carry a table's umbrella title on
        only one page (a title shown once, not repeated), or repeat it
        with a minor per-page variation (e.g. a trailing page number).
        Stripping the umbrella is only safe when there is at most one
        distinguishing title actually in play:
        - both tables have an umbrella: only trust the match if the two
          titles are still recognizably the same title - otherwise two
          unrelated tables sharing a generic deeper header (e.g.
          "Parameter | Value") would look identical once each one's own
          distinguishing title is thrown away.
        - only one table has an umbrella: there is only one title to
          lose, so comparing its stripped form against the other table's
          (already title-less) header carries no such risk.
        """
        previous_umbrella = self.header_signature_builder.umbrella_text(previous_table)
        current_umbrella = self.header_signature_builder.umbrella_text(current_table)
        if previous_umbrella and current_umbrella:
            if not self._tokens_overlap_enough(previous_umbrella, current_umbrella):
                return False
        elif not previous_umbrella and not current_umbrella:
            return False

        previous_collapsed = self._joined_path_text(
            self.header_signature_builder.build_umbrella_collapsed_paths(previous_table)
        )
        current_collapsed = self._joined_path_text(
            self.header_signature_builder.build_umbrella_collapsed_paths(current_table)
        )
        if not previous_collapsed or not current_collapsed:
            return False
        if previous_collapsed == current_collapsed:
            return True
        return self._tokens_overlap_enough(previous_collapsed, current_collapsed)

    @staticmethod
    def _tokens_overlap_enough(previous_text: str, current_text: str) -> bool:
        previous_tokens = set(normalize_table_header_text(previous_text).split())
        current_tokens = set(normalize_table_header_text(current_text).split())
        if not previous_tokens or not current_tokens:
            return False
        overlap = len(previous_tokens & current_tokens)
        longest = max(len(previous_tokens), len(current_tokens))
        return longest > 0 and overlap / longest >= 0.8

    @staticmethod
    def _joined_path_text(header_paths: tuple[tuple[str, ...], ...]) -> str | None:
        if not header_paths:
            return None
        header_parts = []
        for path in header_paths:
            normalized_path = [
                normalize_table_header_text(part)
                for part in path
                if normalize_table_header_text(part)
            ]
            if normalized_path:
                header_parts.extend(normalized_path)
        if not header_parts:
            return None
        return " ".join(header_parts)
