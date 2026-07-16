from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_type_detector import (
    PromptTableTypeDetector,
)


def _source(**overrides) -> PromptSourceView:
    defaults = dict(
        source_number=1,
        chunk_id="chunk_001",
        chunk_type=None,
        section_path="N/A",
        table_shape=None,
        metadata={},
    )
    defaults.update(overrides)
    return PromptSourceView(**defaults)


def test_detect_maps_maintenance_schedule_matrix_shape_to_maintenance_table() -> None:
    source = _source(table_shape="maintenance_schedule_matrix")

    assert PromptTableTypeDetector().detect(source, headers=[]) == "maintenance_table"


def test_detect_maps_performance_curve_matrix_shape_to_specification_table() -> None:
    source = _source(table_shape="performance_curve_matrix")

    assert (
        PromptTableTypeDetector().detect(source, headers=["RPM", "Flow"])
        == "specification_table"
    )


def test_detect_maps_maintenance_interval_table_category_to_maintenance_table() -> None:
    source = _source(metadata={"table_category": "maintenance_interval_table"})

    assert PromptTableTypeDetector().detect(source, headers=[]) == "maintenance_table"


def test_detect_maps_certification_table_category_to_certification_table() -> None:
    source = _source(metadata={"table_category": "certification_table"})

    assert PromptTableTypeDetector().detect(source, headers=[]) == "certification_table"


def test_detect_maps_spare_parts_table_category_to_spare_parts_table() -> None:
    source = _source(metadata={"table_category": "spare_parts_table"})

    assert PromptTableTypeDetector().detect(source, headers=[]) == "spare_parts_table"


def test_detect_residual_maps_technical_data_table_category_to_specification_table() -> None:
    """This residual check has no equivalent in the shared core -- it is
    prompt-only and deliberately kept out of it, since the answer path
    groups this category into its generic record-table bucket instead."""
    source = _source(metadata={"table_category": "technical_data_table"})

    assert PromptTableTypeDetector().detect(source, headers=[]) == "specification_table"


def test_detect_residual_falls_back_to_section_path_certificate_check() -> None:
    source = _source(section_path="Certificate Particulars")

    assert PromptTableTypeDetector().detect(source, headers=[]) == "certification_table"


def test_detect_residual_falls_back_to_header_text_maintenance_keywords() -> None:
    source = _source()

    assert (
        PromptTableTypeDetector().detect(source, headers=["Task", "Interval"])
        == "maintenance_table"
    )


def test_detect_returns_general_table_when_nothing_matches() -> None:
    source = _source()

    assert PromptTableTypeDetector().detect(source, headers=["A", "B"]) == "general_table"


def test_detect_now_covers_toc_table_category_via_shared_core() -> None:
    """Newly-covered by the shared resolution core -- same output as
    before (falls through to general_table), now a considered decision."""
    source = _source(metadata={"table_category": "toc_table"})

    assert PromptTableTypeDetector().detect(source, headers=[]) == "general_table"
