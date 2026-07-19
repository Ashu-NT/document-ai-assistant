from __future__ import annotations

from typing import Protocol

from src.application.langgraph.reflection.strategies.clarification.clarification_context import (
    ClarificationContext,
)


class ClarificationStrategy(Protocol):
    """Proposes clarification options for one `RetrievalQueryIntent`
    category, or, for the generic default, for any category with no
    registered specialization. Replaces the hardcoded per-domain branches
    in the retired `ClarificationBuilder._resolve_options()`."""

    def build_options(self, context: ClarificationContext) -> list[str]: ...
