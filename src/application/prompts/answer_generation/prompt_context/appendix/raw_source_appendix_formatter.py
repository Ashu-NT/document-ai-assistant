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
        if context is None:
            return ""
        sources = self.raw_source_inclusion_policy.select(context)
        if not sources:
            return ""
        return "\n\n".join(
            self._format_source_block(source) for source in sources
        )

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
