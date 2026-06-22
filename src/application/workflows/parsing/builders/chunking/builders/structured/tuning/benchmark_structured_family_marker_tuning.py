from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_marker_tuning import (
    StructuredFamilyMarkerTuning,
)


class BenchmarkStructuredFamilyMarkerTuning(StructuredFamilyMarkerTuning):
    _EXTRA_MARKERS: dict[StructuredEvidenceFamily, tuple[str, ...]] = {
        StructuredEvidenceFamily.DATASHEET_ORDERING_EXAMPLE: ("mk311",),
        StructuredEvidenceFamily.DRAWING_LABEL_BLOCK: (
            "3540.6000",
            "3540.7000",
        ),
        StructuredEvidenceFamily.MANUAL_SPARE_PARTS: (
            "p33",
            "jam release wrench",
        ),
        StructuredEvidenceFamily.SENSOR_LIST: ("lmt100",),
    }

    def extra_markers_for(
        self,
        family: StructuredEvidenceFamily,
    ) -> tuple[str, ...]:
        return self._EXTRA_MARKERS.get(family, ())
