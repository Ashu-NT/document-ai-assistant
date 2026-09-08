import json
from pathlib import Path

from src.application.evaluation.profile_calibration.models.profile_calibration_case_result import (
    ProfileCalibrationCaseResult,
)

DEFAULT_RESULTS_PATH = Path(
    "outputs/evaluation/profile_calibration/profile_calibration_results.json"
)
DEFAULT_REPORT_PATH = Path(
    "outputs/evaluation/profile_calibration/profile_calibration_report.md"
)


class ProfileCalibrationReportStore:
    """Accumulates ProfileCalibrationCaseResult across separate script runs
    (one document at a time, as the user supplies more labeled documents)
    into a persisted JSON store, keyed by document_label so re-running the
    same document updates its entry instead of duplicating it. Also renders
    a human-readable markdown summary, fully regenerated from the JSON
    store on every write -- the JSON is the source of truth, the markdown
    is a disposable view of it.
    """

    def __init__(
        self,
        *,
        results_path: Path | str = DEFAULT_RESULTS_PATH,
        report_path: Path | str = DEFAULT_REPORT_PATH,
    ) -> None:
        self.results_path = Path(results_path)
        self.report_path = Path(report_path)

    def load(self) -> list[ProfileCalibrationCaseResult]:
        if not self.results_path.exists():
            return []
        raw = json.loads(self.results_path.read_text(encoding="utf-8"))
        return [ProfileCalibrationCaseResult.from_dict(entry) for entry in raw]

    def upsert(self, result: ProfileCalibrationCaseResult) -> list[ProfileCalibrationCaseResult]:
        results = self.load()
        results = [
            existing
            for existing in results
            if existing.document_label != result.document_label
        ]
        results.append(result)
        self._write(results)
        return results

    def _write(self, results: list[ProfileCalibrationCaseResult]) -> None:
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        self.results_path.write_text(
            json.dumps([result.to_dict() for result in results], indent=2),
            encoding="utf-8",
        )
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(render_markdown_report(results), encoding="utf-8")


def render_markdown_report(results: list[ProfileCalibrationCaseResult]) -> str:
    lines = ["# Profile Calibration Report", ""]
    lines.append(
        "Compares the production (OLD, raw-occurrence) evidence formula "
        "against a candidate (NEW, ratio-based) one, both decided through "
        "the SAME unmodified StructuralProfileDecisionPolicy. Neither "
        "production scorer nor decision-policy files are changed by this "
        "report -- see project_structural_profile_calibration memory for "
        "why (n=1 real document isn't enough to also re-tune the "
        "decision-policy thresholds without risking blind tuning)."
    )
    lines.append("")

    old_correct = sum(1 for r in results if r.old_correct)
    new_correct = sum(1 for r in results if r.new_correct)
    lines.append(f"- documents: `{len(results)}`")
    lines.append(f"- OLD formula accuracy: `{old_correct}/{len(results)}`")
    lines.append(f"- NEW formula accuracy: `{new_correct}/{len(results)}`")
    lines.append("")

    lines.append(
        "| document | expected | OLD selected | OLD gap | OLD conf | OLD default | "
        "NEW selected | NEW gap | NEW conf | NEW default |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in results:
        old_mark = "" if r.old_correct else " **WRONG**"
        new_mark = "" if r.new_correct else " **WRONG**"
        lines.append(
            f"| {r.document_label} | {r.expected_profile} "
            f"| {r.old.selected_profile}{old_mark} | {r.old.gap:.2f} | {r.old.confidence:.3f} | {r.old.is_default} "
            f"| {r.new.selected_profile}{new_mark} | {r.new.gap:.2f} | {r.new.confidence:.3f} | {r.new.is_default} |"
        )
    lines.append("")

    for r in results:
        lines.append(f"## {r.document_label}")
        lines.append("")
        lines.append(f"expected: `{r.expected_profile}`")
        lines.append("")
        lines.append("| profile | OLD score | NEW score |")
        lines.append("| --- | --- | --- |")
        for profile in sorted(set(r.old.scores) | set(r.new.scores)):
            lines.append(
                f"| {profile} | {r.old.scores.get(profile, 0.0):.2f} "
                f"| {r.new.scores.get(profile, 0.0):.2f} |"
            )
        lines.append("")

    return "\n".join(lines)
