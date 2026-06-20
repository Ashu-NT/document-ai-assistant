from dataclasses import dataclass, field


@dataclass(slots=True)
class RetrievalBenchmarkWorkflowOutput:
    anchor_chunks: list = field(default_factory=list)
    context_chunks: list = field(default_factory=list)
    used_context_expansion: bool = False


class WorkflowResultAdapter:
    def to_workflow_output(
        self,
        workflow_result,
    ) -> RetrievalBenchmarkWorkflowOutput:
        if hasattr(workflow_result, "retrieval_result"):
            anchor_chunks = list(getattr(workflow_result, "chunks", []))
            context_chunks = list(getattr(workflow_result, "final_chunks", anchor_chunks))
            return RetrievalBenchmarkWorkflowOutput(
                anchor_chunks=anchor_chunks,
                context_chunks=context_chunks,
                used_context_expansion=context_chunks != anchor_chunks,
            )

        if hasattr(workflow_result, "chunks"):
            chunks = list(getattr(workflow_result, "chunks", []))
            return RetrievalBenchmarkWorkflowOutput(
                anchor_chunks=chunks,
                context_chunks=chunks,
                used_context_expansion=False,
            )

        return RetrievalBenchmarkWorkflowOutput()
