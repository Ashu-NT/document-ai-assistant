from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.appendix.raw_source_inclusion_policy import (
    RawSourceInclusionPolicy,
)


class RawSourceAppendixFormatter:
    def __init__(
        self,
        raw_source_inclusion_policy: RawSourceInclusionPolicy | None = None,
    ) -> None:
        self.raw_source_inclusion_policy = (
            raw_source_inclusion_policy or RawSourceInclusionPolicy()
        )

    def format(self, context: PromptContextBundle | None) -> str:
        text, _ = self.format_with_selection(context)
        return text

    def format_with_selection(
        self, context: PromptContextBundle | None
    ) -> tuple[str, list[int]]:
        """Same as `format()`, but also returns the source_number values
        that were actually selected into the raw-prose appendix under the
        budget -- needed so callers can tell "shown as text" apart from
        "merely listed in the structured JSON payload" (see
        RawSourceInclusionPolicy.select()).
        """
        text, source_numbers, _diagnostics = self.format_with_diagnostics(context)
        return text, source_numbers

    def format_with_diagnostics(
        self, context: PromptContextBundle | None
    ) -> tuple[str, list[int], dict[str, object]]:
        """Same as `format_with_selection()`, but also returns the raw
        appendix's truncation diagnostics (PR 8, W6,
        answering_flow_weakness_remediation_plan.md)."""
        if context is None:
            return "", [], {}
        sources, diagnostics = self.raw_source_inclusion_policy.select_with_diagnostics(
            context
        )
        if not sources:
            return "", [], diagnostics
        text = "\n\n".join(self._format_source_block(source) for source in sources)
        return text, [source.source_number for source in sources], diagnostics

    def _format_source_block(self, source: PromptSourceView) -> str:
        page_range = self._format_page_bounds(source.page_start, source.page_end)
        return (
            f"SOURCE {source.source_number}\n"
            f"Document: {source.document_title}\n"
            f"Section: {source.section_path}\n"
            f"Pages: {page_range}\n"
            "---\n"
            f"{source.content}"
        )

    @staticmethod
    def _format_page_bounds(
        page_start: int | None,
        page_end: int | None,
    ) -> str:
        if page_start is None and page_end is None:
            return "N/A"
        if page_start == page_end:
            return str(page_start)
        if page_start is None:
            return str(page_end)
        if page_end is None:
            return str(page_start)
        return f"{page_start}-{page_end}"
