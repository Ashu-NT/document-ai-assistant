from src.application.workflows.question_answering.question_answering_request import (
    QuestionAnsweringRequest,
)
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.application.workflows.retrieval.structured import (
    StructuredEvidenceBundle,
    StructuredEvidenceResolver,
)
from src.application.workflows.shared.structured_evidence_deduplication import (
    deduplicate_identifiers,
    deduplicate_structured_entities,
)
from src.domain.retrieval import RetrievalQuery


class StructuredEvidenceMerger:
    """Merges the identifiers/structured entities the caller already
    resolved (`request.resolved_identifiers`/`resolved_structured_entities`)
    with whatever structured evidence the retrieval workflow itself
    surfaced, falling back to a dedicated resolver when retrieval found
    none -- so downstream steps always see one deduplicated bundle
    regardless of which path produced the evidence."""

    def __init__(
        self,
        structured_evidence_resolver: StructuredEvidenceResolver | None = None,
    ) -> None:
        self._structured_evidence_resolver = structured_evidence_resolver

    def merge(
        self,
        *,
        request: QuestionAnsweringRequest,
        analyzed_query: RetrievalQuery,
        workflow_result: RetrievalWorkflowResult,
    ) -> StructuredEvidenceBundle:
        resolved_identifiers = deduplicate_identifiers(
            list(request.resolved_identifiers)
        )
        resolved_structured_entities = deduplicate_structured_entities(
            list(request.resolved_structured_entities)
        )
        workflow_bundle = workflow_result.structured_evidence

        if workflow_bundle is None and self._structured_evidence_resolver is not None:
            workflow_bundle = self._structured_evidence_resolver.resolve(analyzed_query)

        if workflow_bundle is None:
            return StructuredEvidenceBundle(
                identifiers=resolved_identifiers,
                structured_entities=resolved_structured_entities,
            )

        return StructuredEvidenceBundle(
            identifiers=deduplicate_identifiers(
                [*resolved_identifiers, *workflow_bundle.identifiers]
            ),
            structured_entities=deduplicate_structured_entities(
                [*resolved_structured_entities, *workflow_bundle.structured_entities]
            ),
            chunks=list(workflow_bundle.chunks),
            diagnostics=dict(workflow_bundle.diagnostics),
        )
