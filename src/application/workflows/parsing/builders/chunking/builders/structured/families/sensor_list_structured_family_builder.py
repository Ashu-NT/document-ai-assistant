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
        specs: list[StructuredSectionWindowSpec] = []
        for family, label, markers in [
            (
                StructuredEvidenceFamily.SENSOR_LIST,
                "Sensor List",
                SENSOR_LIST_MARKERS,
            ),
            (
                StructuredEvidenceFamily.INSTRUMENT_LIST,
                "Instrument List",
                INSTRUMENT_LIST_MARKERS,
            ),
            (
                StructuredEvidenceFamily.TAG_LIST,
                "Tag List",
                TAG_LIST_MARKERS,
            ),
            (
                StructuredEvidenceFamily.PID_LIST,
                "P&ID List",
                PID_LIST_MARKERS,
            ),
            (
                StructuredEvidenceFamily.IO_LIST,
                "I/O List",
                IO_LIST_MARKERS,
            ),
        ]:
            if not self._should_include_family(
                base_path=base_path,
                label=label,
                context=context,
                markers=markers,
            ):
                continue
            specs.append(
                StructuredSectionWindowSpec(
                    family=family,
                    section_path=self._path_for_label(base_path, label),
                    anchor_markers=extend_markers(
                        family=family,
                        base_markers=markers,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                )
            )
        return StructuredFamilySpecSelection(specs=specs)

    @staticmethod
    def _path_for_label(
        base_path: list[str],
        label: str,
    ) -> list[str]:
        markers = (label.lower(),)
        return base_path if path_contains_markers(base_path, markers) else [label]

    @staticmethod
    def _should_include_family(
        *,
        base_path: list[str],
        label: str,
        context: StructuredFamilyContext,
        markers: tuple[str, ...],
    ) -> bool:
        label_markers = (label.lower(),)
        if path_contains_markers(base_path, label_markers):
            return True
        if any(
            path_contains_markers(
                base_path,
                (other_label.lower(),),
            )
            for other_label in (
                "Sensor List",
                "Instrument List",
                "Tag List",
                "P&ID List",
                "I/O List",
            )
        ):
            return False
        return context.contains_any(markers)
