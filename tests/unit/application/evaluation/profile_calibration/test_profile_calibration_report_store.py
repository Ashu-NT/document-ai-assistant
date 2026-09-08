from src.application.evaluation.profile_calibration.models.profile_calibration_case_result import (
    ProfileCalibrationCaseResult,
)
from src.application.evaluation.profile_calibration.models.profile_scoring_snapshot import (
    ProfileScoringSnapshot,
)
from src.application.evaluation.profile_calibration.profile_calibration_report_store import (
    ProfileCalibrationReportStore,
    render_markdown_report,
)


def _make_result(label: str, selected: str = "manual") -> ProfileCalibrationCaseResult:
    snapshot = ProfileScoringSnapshot(
        scores={"manual": 8.0, "datasheet": 1.0, "drawing": 0.0, "report": 0.0, "certificate": 0.0, "default": 0.0},
        selected_profile=selected,
        confidence=0.8,
        top_score=8.0,
        second_score=1.0,
        gap=7.0,
        is_default=False,
    )
    return ProfileCalibrationCaseResult(
        document_label=label,
        expected_profile="manual",
        old=snapshot,
        new=snapshot,
    )


def test_upsert_persists_and_reloads(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )

    store.upsert(_make_result("doc-a"))
    results = store.load()

    assert len(results) == 1
    assert results[0].document_label == "doc-a"


def test_upsert_replaces_same_label_instead_of_duplicating(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )

    store.upsert(_make_result("doc-a", selected="manual"))
    store.upsert(_make_result("doc-a", selected="datasheet"))
    results = store.load()

    assert len(results) == 1
    assert results[0].old.selected_profile == "datasheet"


def test_upsert_accumulates_distinct_labels(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )

    store.upsert(_make_result("doc-a"))
    store.upsert(_make_result("doc-b"))
    results = store.load()

    assert {r.document_label for r in results} == {"doc-a", "doc-b"}


def test_render_markdown_report_includes_accuracy_summary() -> None:
    results = [_make_result("doc-a", selected="manual"), _make_result("doc-b", selected="datasheet")]

    report = render_markdown_report(results)

    assert "OLD formula accuracy: `1/2`" in report
    assert "doc-a" in report
    assert "doc-b" in report
