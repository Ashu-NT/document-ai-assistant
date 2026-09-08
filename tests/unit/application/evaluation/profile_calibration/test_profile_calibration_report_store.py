from src.application.evaluation.profile_calibration.models.profile_calibration_case_result import (
    ProfileCalibrationCaseResult,
)
from src.application.evaluation.profile_calibration.models.profile_evidence_diagnostics import (
    ProfileEvidenceDiagnostics,
)
from src.application.evaluation.profile_calibration.models.profile_scoring_snapshot import (
    ProfileScoringSnapshot,
)
from src.application.evaluation.profile_calibration.profile_calibration_report_store import (
    ProfileCalibrationReportStore,
    render_markdown_report,
)


def _make_result(
    label: str,
    *,
    document_hash: str | None = None,
    selected: str = "manual",
) -> ProfileCalibrationCaseResult:
    snapshot = ProfileScoringSnapshot(
        scores={"manual": 8.0, "datasheet": 1.0, "drawing": 0.0, "report": 0.0, "certificate": 0.0, "default": 0.0},
        selected_profile=selected,
        second_profile="datasheet",
        confidence=0.8,
        top_score=8.0,
        second_score=1.0,
        gap=7.0,
        is_default=False,
    )
    return ProfileCalibrationCaseResult(
        document_label=label,
        document_hash=document_hash if document_hash is not None else f"hash-{label}",
        expected_profile="manual",
        section_count=42,
        evidence_diagnostics={
            "manual": ProfileEvidenceDiagnostics(
                total_occurrences=6, distinct_term_count=3, matching_title_count=4
            )
        },
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
    assert results[0].section_count == 42
    assert results[0].evidence_diagnostics["manual"].total_occurrences == 6


def test_upsert_replaces_same_document_hash_instead_of_duplicating(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )

    store.upsert(_make_result("doc-a", document_hash="hash-1", selected="manual"))
    store.upsert(_make_result("doc-a", document_hash="hash-1", selected="datasheet"))
    results = store.load()

    assert len(results) == 1
    assert results[0].old.selected_profile == "datasheet"


def test_upsert_accumulates_distinct_hashes(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )

    store.upsert(_make_result("doc-a", document_hash="hash-1"))
    store.upsert(_make_result("doc-b", document_hash="hash-2"))
    results = store.load()

    assert {r.document_hash for r in results} == {"hash-1", "hash-2"}


def test_remove_drops_the_case_and_leaves_others_intact(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )
    store.upsert(_make_result("doc-a", document_hash="hash-1"))
    store.upsert(_make_result("doc-b", document_hash="hash-2"))

    remaining = store.remove("hash-1")

    assert {r.document_hash for r in remaining} == {"hash-2"}
    assert {r.document_hash for r in store.load()} == {"hash-2"}


def test_remove_unknown_hash_is_a_no_op(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )
    store.upsert(_make_result("doc-a", document_hash="hash-1"))

    remaining = store.remove("hash-does-not-exist")

    assert {r.document_hash for r in remaining} == {"hash-1"}


def test_same_label_different_hash_does_not_collide(tmp_path) -> None:
    """Safeguard: identity is document_hash, not the human label -- two
    genuinely different documents that happen to share a label must both
    survive, not silently overwrite each other."""
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )

    store.upsert(_make_result("Manual", document_hash="hash-1"))
    store.upsert(_make_result("Manual", document_hash="hash-2"))
    results = store.load()

    assert len(results) == 2
    assert {r.document_hash for r in results} == {"hash-1", "hash-2"}


def test_renaming_a_label_for_the_same_hash_updates_in_place(tmp_path) -> None:
    store = ProfileCalibrationReportStore(
        results_path=tmp_path / "results.json",
        report_path=tmp_path / "report.md",
    )

    store.upsert(_make_result("Old Name", document_hash="hash-1"))
    store.upsert(_make_result("New Name", document_hash="hash-1"))
    results = store.load()

    assert len(results) == 1
    assert results[0].document_label == "New Name"


def test_render_markdown_report_includes_accuracy_summary() -> None:
    results = [
        _make_result("doc-a", document_hash="hash-1", selected="manual"),
        _make_result("doc-b", document_hash="hash-2", selected="datasheet"),
    ]

    report = render_markdown_report(results)

    assert "OLD formula accuracy: `1/2`" in report
    assert "doc-a" in report
    assert "doc-b" in report
    assert "hash-1"[:12] in report
