from collections.abc import Callable


class OverviewSubsectionSummaryBuilder:
    """Builds an honest, token-bounded summary of direct child sections."""

    def __init__(self, *, count_tokens: Callable[[str], int]) -> None:
        self.count_tokens = count_tokens

    def build(self, titles: list[str], *, max_tokens: int) -> str | None:
        if not titles or max_tokens <= 0:
            return None

        total = len(titles)
        full_summary = f"Direct subsections ({total}): {'; '.join(titles)}"
        if self.count_tokens(full_summary) <= max_tokens:
            return full_summary

        for included_count in range(total - 1, 0, -1):
            omitted_count = total - included_count
            candidate = (
                f"Direct subsections ({total}): "
                f"{'; '.join(titles[:included_count])}; "
                f"[{omitted_count} omitted due to token limit]"
            )
            if self.count_tokens(candidate) <= max_tokens:
                return candidate

        count_only = (
            f"Direct subsections: {total} total; "
            "titles omitted due to token limit."
        )
        if self.count_tokens(count_only) <= max_tokens:
            return count_only
        return None
