from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    append_label_if_missing,
    extend_markers,
    path_contains_markers,
    sanitized_base_path,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    DATASHEET_COOLING_SYSTEM_MARKERS,
    DATASHEET_CONNECTION_INFORMATION_MARKERS,
    DATASHEET_DOCUMENT_MARKERS,
    DATASHEET_INSTALLATION_MAINTENANCE_MARKERS,
    DATASHEET_MATERIAL_INFORMATION_MARKERS,
    DATASHEET_OPERATING_LIMITS_MARKERS,
    DATASHEET_ORDERING_EXAMPLE_MARKERS,
    DATASHEET_ORDERING_INFORMATION_MARKERS,
    DATASHEET_PRESSURE_TEMPERATURE_MARKERS,
    DATASHEET_PRODUCT_OVERVIEW_MARKERS,
    DATASHEET_SENSOR_INFORMATION_MARKERS,
    DATASHEET_SPECIFICATION_TABLE_MARKERS,
    DATASHEET_TECHNICAL_DATA_MARKERS,
    DATASHEET_TECHNICAL_FEATURES_MARKERS,
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
from src.domain.common import ChunkType, DocumentType

_PRODUCT_OVERVIEW_PATH_MARKERS = ("product overview",)
_TECHNICAL_FEATURES_PATH_MARKERS = ("technical features", "caratteristiche tecniche")
_COOLING_SYSTEM_PATH_MARKERS = ("cooling system",)
_SENSOR_INFORMATION_PATH_MARKERS = ("sensor", "sensors")
_INSTALLATION_MAINTENANCE_PATH_MARKERS = (
    "installation instructions",
    "installation and maintenance",
    "mounting and maintenance",
    "montaggio",
    "manutenzione",
)
_EMBEDDED_DATASHEET_REGION_MARKERS = (
    "datasheet",
    "product overview",
    "technical data",
    "technical features",
    "ordering information",
    "ordering example",
    "cooling system",
    "installation instructions",
    "operating limits",
    "pressure-temperature diagram",
    "pressure temperature diagram",
)


class DatasheetStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if context.matches_document_type(DocumentType.DATASHEET):
            pass
        elif context.has_known_document_type():
            if not self._has_embedded_datasheet_signal(context):
                return StructuredFamilySpecSelection()
        elif not context.contains_any(DATASHEET_DOCUMENT_MARKERS):
            return StructuredFamilySpecSelection()

        base_path = sanitized_base_path(
            section_path=context.base_section_path(),
            section_title=context.section.title,
            document_title=context.document_title,
        )

        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_PRODUCT_OVERVIEW,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_PRODUCT_OVERVIEW_PATH_MARKERS,
                        label="Product overview",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_PRODUCT_OVERVIEW,
                        base_markers=DATASHEET_PRODUCT_OVERVIEW_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path,
                        _PRODUCT_OVERVIEW_PATH_MARKERS,
                    ),
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_TECHNICAL_DATA,
                    section_path=["Technical Data / Specification"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_TECHNICAL_DATA,
                        base_markers=DATASHEET_TECHNICAL_DATA_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_TECHNICAL_FEATURES,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_TECHNICAL_FEATURES_PATH_MARKERS,
                        label="Technical features",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_TECHNICAL_FEATURES,
                        base_markers=DATASHEET_TECHNICAL_FEATURES_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=14,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path,
                        _TECHNICAL_FEATURES_PATH_MARKERS,
                    ),
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_SPECIFICATION_TABLE,
                    section_path=["Technical Data / Specification"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_SPECIFICATION_TABLE,
                        base_markers=DATASHEET_SPECIFICATION_TABLE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_ORDERING_INFORMATION,
                    section_path=["Ordering information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_ORDERING_INFORMATION,
                        base_markers=DATASHEET_ORDERING_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=10,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_ORDERING_EXAMPLE,
                    section_path=["Ordering example"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_ORDERING_EXAMPLE,
                        base_markers=DATASHEET_ORDERING_EXAMPLE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=2,
                    radius_after=10,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_CONNECTION_INFORMATION,
                    section_path=["CONNECTION"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_CONNECTION_INFORMATION,
                        base_markers=DATASHEET_CONNECTION_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=10,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_COOLING_SYSTEM,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_COOLING_SYSTEM_PATH_MARKERS,
                        label="Cooling system",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_COOLING_SYSTEM,
                        base_markers=DATASHEET_COOLING_SYSTEM_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path,
                        _COOLING_SYSTEM_PATH_MARKERS,
                    ),
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_SENSOR_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_SENSOR_INFORMATION_PATH_MARKERS,
                        label="Sensors",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_SENSOR_INFORMATION,
                        base_markers=DATASHEET_SENSOR_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path,
                        _SENSOR_INFORMATION_PATH_MARKERS,
                    ),
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_OPERATING_LIMITS,
                    section_path=["Operating limits"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_OPERATING_LIMITS,
                        base_markers=DATASHEET_OPERATING_LIMITS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_PRESSURE_TEMPERATURE_DATA,
                    section_path=[
                        "Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram"
                    ],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_PRESSURE_TEMPERATURE_DATA,
                        base_markers=DATASHEET_PRESSURE_TEMPERATURE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=2,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_MATERIAL_INFORMATION,
                    section_path=["Material information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_MATERIAL_INFORMATION,
                        base_markers=DATASHEET_MATERIAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=10,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_INSTALLATION_MAINTENANCE,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_INSTALLATION_MAINTENANCE_PATH_MARKERS,
                        label="Installation instructions and maintenance",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_INSTALLATION_MAINTENANCE,
                        base_markers=DATASHEET_INSTALLATION_MAINTENANCE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path,
                        _INSTALLATION_MAINTENANCE_PATH_MARKERS,
                    ),
                ),
            ]
        )

    @staticmethod
    def _family_section_path(
        *,
        base_path: list[str],
        family_markers: tuple[str, ...],
        label: str,
    ) -> list[str]:
        if path_contains_markers(base_path, family_markers):
            return base_path
        return append_label_if_missing(base_path, label)

    @staticmethod
    def _has_embedded_datasheet_signal(
        context: StructuredFamilyContext,
    ) -> bool:
        return context.section_contains_any(
            _EMBEDDED_DATASHEET_REGION_MARKERS
        ) or context.content_contains_any(
            _EMBEDDED_DATASHEET_REGION_MARKERS
        )
