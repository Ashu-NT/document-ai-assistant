from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)


class StructuredFamilyMarkerTuning:
    def extra_markers_for(
        self,
        family: StructuredEvidenceFamily,
    ) -> tuple[str, ...]:
        return ()
