from __future__ import annotations

from src.application.langgraph.reflection.strategies.clarification.clarification_context import (
    ClarificationContext,
)

_GENERIC_FALLBACK_OPTIONS = (
    "the exact section",
    "the exact procedure",
    "the exact specification",
)


class FixedOptionsClarificationStrategy:
    """The one clarification strategy class, shared by the generic default
    and every registered domain intent -- the only thing that differs is
    `fixed_options` (`None` for generic). Migrated 1:1 from the retired
    `ClarificationBuilder._resolve_options()`: a registered domain intent
    always proposes its fixed options; the generic default proposes
    `missing_information` when available, else a generic fallback."""

    def __init__(self, *, fixed_options: tuple[str, ...] | None = None) -> None:
        self._fixed_options = fixed_options

    def build_options(self, context: ClarificationContext) -> list[str]:
        if self._fixed_options is not None:
            return list(self._fixed_options)
        if context.missing_information:
            return list(context.missing_information[:3])
        return list(_GENERIC_FALLBACK_OPTIONS)
