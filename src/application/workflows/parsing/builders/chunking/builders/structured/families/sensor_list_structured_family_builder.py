from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    extend_markers,
    path_contains_markers,
    sanitized_base_path,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    INSTRUMENT_LIST_MARKERS,
    IO_LIST_MARKERS,
    PID_LIST_MARKERS,
    SENSOR_DOCUMENT_MARKERS,
    SENSOR_LIST_MARKERS,
    TAG_LIST_MARKERS,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_context import (
    StructuredFamilyContext,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_marker_tuning import (
    StructuredFamilyMarkerTuning,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_spec_selection import (
    StructuredFamilySpecSelection,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.domain.common import ChunkType


class SensorListStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if not context.contains_any(SENSOR_DOCUMENT_MARKERS):
            return StructuredFamilySpecSelection()

        base_path = sanitized_base_path(
            section_path=context.base_section_path(),
            section_title=context.section.title,
            document_title=context.document_title,
        )
        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.SENSOR_LIST,
                    section_path=self._path_for_label(base_path, "Sensor List"),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.SENSOR_LIST,
                        base_markers=SENSOR_LIST_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.INSTRUMENT_LIST,
                    section_path=self._path_for_label(base_path, "Instrument List"),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.INSTRUMENT_LIST,
                        base_markers=INSTRUMENT_LIST_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.TAG_LIST,
                    section_path=self._path_for_label(base_path, "Tag List"),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.TAG_LIST,
                        base_markers=TAG_LIST_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.PID_LIST,
                    section_path=self._path_for_label(base_path, "P&ID List"),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.PID_LIST,
                        base_markers=PID_LIST_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.IO_LIST,
                    section_path=self._path_for_label(base_path, "I/O List"),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.IO_LIST,
                        base_markers=IO_LIST_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
            ]
        )

    @staticmethod
    def _path_for_label(
        base_path: list[str],
        label: str,
    ) -> list[str]:
        markers = (label.lower(),)
        return base_path if path_contains_markers(base_path, markers) else [label]
