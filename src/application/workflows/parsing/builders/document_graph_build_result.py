from dataclasses import dataclass

from src.application.workflows.parsing.builders.document_graph.cross_references import (
    CrossReferenceLinkingOutcome,
)
from src.domain.document import DocumentGraph


@dataclass(slots=True, frozen=True)
class DocumentGraphBuildResult:
    """What DocumentGraphBuilder.build() returns: the built graph plus the
    cross-reference linking/reconciliation outcome, bundled explicitly
    instead of stashed on a `last_cross_reference_linking_outcome`
    instance attribute - callers that need the outcome (e.g. corpus
    verification scripts) read it from this return value, not from
    builder instance state that a concurrently-reused builder instance
    could overwrite between write and read."""

    graph: DocumentGraph
    cross_reference_linking_outcome: CrossReferenceLinkingOutcome | None = None


__all__ = ["DocumentGraphBuildResult"]
