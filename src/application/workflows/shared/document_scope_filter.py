from __future__ import annotations

# Canonical "does this chunk belong to the requested document scope" filter,
# previously reimplemented independently in RetrievalWorkflow._enforce_document_scope
# and QuestionAnsweringWorkflow._document_scope_violation. Both callers only
# differ in what they do with the rejected/leaking chunks afterward (one
# tracks them for diagnostics, the other treats any non-empty rejection as a
# guardrail violation) -- the partition itself was identical.
def partition_chunks_by_document_scope(
    chunks: list,
    document_id: str | None,
) -> tuple[list, list]:
    if document_id is None:
        return list(chunks), []

    approved = [chunk for chunk in chunks if chunk.document_id == document_id]
    rejected = [chunk for chunk in chunks if chunk.document_id != document_id]
    return approved, rejected
