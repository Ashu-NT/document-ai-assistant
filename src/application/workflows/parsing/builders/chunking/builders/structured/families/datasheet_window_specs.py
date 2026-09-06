from src.application.workflows.parsing.builders.chunking.builders.structured.families.datasheet_family_helpers import (
    family_section_path,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    extend_markers,
    path_contains_terms,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    DATASHEET_COOLING_SYSTEM_MARKERS,
    DATASHEET_CONNECTION_INFORMATION_MARKERS,
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
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_marker_tuning import (
    StructuredFamilyMarkerTuning,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.domain.common import ChunkType

PRODUCT_OVERVIEW_PATH_MARKERS = ("product overview",)
TECHNICAL_FEATURES_PATH_MARKERS = ("technical features", "caratteristiche tecniche")
COOLING_SYSTEM_PATH_MARKERS = ("cooling system",)
SENSOR_INFORMATION_PATH_MARKERS = ("sensor", "sensors")
INSTALLATION_MAINTENANCE_PATH_MARKERS = (
    "installation instructions",
    "installation and maintenance",
    "mounting and maintenance",
    "montaggio",
    "manutenzione",
)


def build_datasheet_window_specs(
    *,
    base_path: list[str],
    marker_tuning: StructuredFamilyMarkerTuning | None,
) -> list[StructuredSectionWindowSpec]:
    return [
        StructuredSectionWindowSpec(
            family=StructuredEvidenceFamily.DATASHEET_PRODUCT_OVERVIEW,
            section_path=family_section_path(
                base_path=base_path,
                family_markers=PRODUCT_OVERVIEW_PATH_MARKERS,
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
            include_full_section_if_no_anchor=path_contains_terms(
                base_path,
                PRODUCT_OVERVIEW_PATH_MARKERS,
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
            section_path=family_section_path(
                base_path=base_path,
                family_markers=TECHNICAL_FEATURES_PATH_MARKERS,
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
            include_full_section_if_no_anchor=path_contains_terms(
                base_path,
                TECHNICAL_FEATURES_PATH_MARKERS,
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
            section_path=family_section_path(
                base_path=base_path,
                family_markers=COOLING_SYSTEM_PATH_MARKERS,
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
            include_full_section_if_no_anchor=path_contains_terms(
                base_path,
                COOLING_SYSTEM_PATH_MARKERS,
            ),
        ),
        StructuredSectionWindowSpec(
            family=StructuredEvidenceFamily.DATASHEET_SENSOR_INFORMATION,
            section_path=family_section_path(
                base_path=base_path,
                family_markers=SENSOR_INFORMATION_PATH_MARKERS,
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
            include_full_section_if_no_anchor=path_contains_terms(
                base_path,
                SENSOR_INFORMATION_PATH_MARKERS,
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
            section_path=["Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram"],
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
            section_path=family_section_path(
                base_path=base_path,
                family_markers=INSTALLATION_MAINTENANCE_PATH_MARKERS,
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
            include_full_section_if_no_anchor=path_contains_terms(
                base_path,
                INSTALLATION_MAINTENANCE_PATH_MARKERS,
            ),
        ),
    ]
