from __future__ import annotations

from src.application.validation.document_quality import DocumentQualityGate


class QualityCheckStep:
    """Runs the post-ingestion parsing/chunking quality gate against a
    finalized document graph, appending any check failures to the run's
    warnings list and returning a summary diagnostics payload.
    """

    def __init__(self, *, quality_gate: DocumentQualityGate) -> None:
        self.quality_gate = quality_gate

    def run(
        self,
        *,
        parsing_result,
        final_graph,
        warnings: list[str],
    ) -> dict[str, object]:
        parsing_quality = self.quality_gate.check_parsing(
            final_graph.document.document_id,
            sections=list(final_graph.sections.values()),
            elements=list(final_graph.elements.values()),
            ocr_trace=parsing_result.ocr_trace,
        )
        chunking_quality = self.quality_gate.check_chunking(
            final_graph.document.document_id,
            chunks=list(final_graph.chunks.values()),
        )
        for quality_result in (parsing_quality, chunking_quality):
            for check in quality_result.failures():
                warnings.append(f"{check.check_name}: {check.message}")
        return {
            "parsing_quality": parsing_quality.summary(),
            "chunking_quality": chunking_quality.summary(),
        }
