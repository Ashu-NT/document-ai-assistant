from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_marker_tuning import (
    StructuredFamilyMarkerTuning,
)


class BenchmarkStructuredFamilyMarkerTuning(StructuredFamilyMarkerTuning):
    _EXTRA_MARKERS: dict[
        StructuredEvidenceFamily,
        tuple[EvidenceMarker, ...],
    ] = {
        StructuredEvidenceFamily.DATASHEET_ORDERING_EXAMPLE: (
            EvidenceMarker(
                "mk311",
                MarkerStrength.STRONG,
            ),
        ),
        StructuredEvidenceFamily.DRAWING_LABEL_BLOCK: (
            EvidenceMarker(
                "3540.6000",
                MarkerStrength.STRONG,
            ),
            EvidenceMarker(
                "3540.7000",
                MarkerStrength.STRONG,
            ),
        ),
        StructuredEvidenceFamily.MANUAL_SPARE_PARTS: (
            EvidenceMarker(
                "p33",
                MarkerStrength.MEDIUM,
            ),
            EvidenceMarker(
                "jam release wrench",
                MarkerStrength.STRONG,
            ),
        ),
        StructuredEvidenceFamily.SENSOR_LIST: (
            EvidenceMarker(
                "lmt100",
                MarkerStrength.STRONG,
            ),
        ),
    }

    def extra_markers_for(
        self,
        family: StructuredEvidenceFamily,
    ) -> tuple[EvidenceMarker, ...]:
        return self._EXTRA_MARKERS.get(
            family,
            (),
        )