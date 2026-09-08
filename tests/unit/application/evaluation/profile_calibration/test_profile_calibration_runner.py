from src.application.evaluation.profile_calibration.profile_calibration_runner import (
    ProfileCalibrationRunner,
)
from src.domain.document import DocumentSection


def _manual_like_sections() -> list[DocumentSection]:
    titles = [
        "Maintenance Procedures",
        "Installation Instructions",
        "Troubleshooting Operations",
        "General Service Notes",
    ]
    return [
        DocumentSection(section_id=f"sec_{i}", document_id="doc_1", title=title)
        for i, title in enumerate(titles)
    ]


def test_run_produces_old_and_new_snapshots_for_a_manual_like_document() -> None:
    runner = ProfileCalibrationRunner()

    result = runner.run(
        document_label="synthetic-manual",
        expected_profile="manual",
        document_title="Pump Field Service Manual",
        sections=_manual_like_sections(),
        section_elements_by_id={},
    )

    assert result.document_label == "synthetic-manual"
    assert result.expected_profile == "manual"
    assert result.old.selected_profile == "manual"
    assert result.new.selected_profile == "manual"
    assert result.old_correct is True
    assert result.new_correct is True


def test_old_and_new_use_the_same_underlying_features() -> None:
    """Both formulas must be scored against the identical extracted
    features -- this is a controlled single-variable comparison, not two
    independently re-extracted feature sets."""
    runner = ProfileCalibrationRunner()

    result = runner.run(
        document_label="doc",
        expected_profile="manual",
        document_title="Pump Field Service Manual",
        sections=_manual_like_sections(),
        section_elements_by_id={},
    )

    # REPORT never had any evidence in either formula for this document, so
    # its score must be identical old vs new -- only manual-evidence-bearing
    # profiles should be able to diverge.
    assert result.old.scores["report"] == result.new.scores["report"]


def test_run_on_an_empty_document_defaults_under_both_formulas() -> None:
    runner = ProfileCalibrationRunner()

    result = runner.run(
        document_label="empty-doc",
        expected_profile="default",
        document_title=None,
        sections=[],
        section_elements_by_id={},
    )

    assert result.old.selected_profile == "default"
    assert result.new.selected_profile == "default"
    assert result.old_correct is True
    assert result.new_correct is True
