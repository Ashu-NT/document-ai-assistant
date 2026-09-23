from src.application.evaluation.golden.golden_evaluation_report import (
    GoldenEvaluationReport,
)


class GoldenEvaluationReportMarkdownRenderer:
    def render(self, report: GoldenEvaluationReport) -> str:
        lines: list[str] = ["# Golden Evaluation", ""]

        lines.extend(self._render_corpus_section(report))
        lines.extend(self._render_structural_section(report))
        lines.extend(self._render_chunking_section(report))
        lines.extend(self._render_cross_reference_section(report))
        lines.extend(self._render_reconciliation_section(report))
        lines.extend(self._render_not_evaluated_section(report))
        lines.extend(self._render_reproducibility_section(report))

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _render_corpus_section(report: GoldenEvaluationReport) -> list[str]:
        coverage = report.corpus_coverage
        return [
            "## Corpus",
            "",
            f"- expected documents: `{coverage.expected}`",
            f"- available: `{coverage.available}`",
            f"- evaluated: `{coverage.evaluated}`",
            "",
        ]

    @staticmethod
    def _render_structural_section(report: GoldenEvaluationReport) -> list[str]:
        return [
            "## Structural",
            "",
            f"- passed documents: `{report.structural_passed_count}`",
            f"- failed documents: `{report.structural_failed_count}`",
            f"- structural assertion failures: `{report.structural_assertion_failure_count}`",
            "",
        ]

    @staticmethod
    def _render_chunking_section(report: GoldenEvaluationReport) -> list[str]:
        lines = [
            "## Chunking",
            "",
            f"- invariant failures: `{report.chunk_invariant_failure_count}`",
            f"- token-budget hard violations: `{report.chunk_token_budget_hard_violation_count}`",
            f"- token-budget oversized-indivisible (informational, not a failure): "
            f"`{report.chunk_token_budget_oversized_indivisible_count}`",
        ]
        if report.chunk_token_budget_unresolved_aliases:
            lines.append(
                "- effective chunking profile could not be resolved for: "
                f"`{', '.join(report.chunk_token_budget_unresolved_aliases)}`"
            )
        lines.append("")

        for outcome in report.document_outcomes:
            result = outcome.chunk_token_budget_result
            if result is None:
                continue
            lines.append(f"### {outcome.alias}")
            lines.append("")
            if not result.resolved:
                lines.append(f"- effective profile: unresolved ({result.unresolved_reason})")
                lines.append("")
                continue
            lines.append(f"- effective profile: `{result.profile}`")
            lines.append(f"- effective budget: `{result.effective_budget}` tokens")
            lines.append(f"- max observed tokens: `{result.max_observed_tokens}`")
            lines.append(f"- normal chunks: `{result.normal_count}`")
            lines.append(
                f"- oversized-indivisible chunks: `{result.oversized_indivisible_count}`"
            )
            lines.append(
                f"- hard budget violations: `{result.hard_budget_violation_count}`"
            )
            if result.oversized_chunks:
                lines.append("")
                lines.append("| chunk_id | status | tokens | budget | chunk_type | table_id | rows |")
                lines.append("| --- | --- | --- | --- | --- | --- | --- |")
                for diagnostic in result.oversized_chunks:
                    rows = (
                        f"{diagnostic.table_row_start}-{diagnostic.table_row_end}"
                        if diagnostic.table_row_start is not None
                        else "n/a"
                    )
                    lines.append(
                        f"| {diagnostic.chunk_id} | {diagnostic.status.value} | "
                        f"{diagnostic.token_count} | {diagnostic.budget} | "
                        f"{diagnostic.chunk_type} | {diagnostic.table_id or 'n/a'} | {rows} |"
                    )
            lines.append("")
        return lines

    @staticmethod
    def _render_cross_reference_section(report: GoldenEvaluationReport) -> list[str]:
        lines = ["## Cross References", ""]
        type_metrics = report.cross_reference_type_metrics
        if not type_metrics:
            lines.extend(["_No curated cross-reference expectations evaluated._", ""])
            return lines

        for metrics in type_metrics:
            precision = (
                f"{metrics.precision:.2f}"
                if metrics.precision is not None
                else "n/a (presence-only annotation)"
            )
            recall = f"{metrics.recall:.2f}" if metrics.recall is not None else "n/a"
            f1 = f"{metrics.f1:.2f}" if metrics.f1 is not None else "n/a"
            lines.extend(
                [
                    f"### {metrics.reference_type}",
                    "",
                    f"- TP: `{metrics.true_positives}`",
                    f"- FP: `{metrics.false_positives if metrics.false_positives is not None else 'n/a (presence-only annotation)'}`",
                    f"- FN: `{metrics.false_negatives}`",
                    f"- Precision: `{precision}`",
                    f"- Recall: `{recall}`",
                    f"- F1: `{f1}`",
                    "",
                ]
            )
        return lines

    @staticmethod
    def _render_reconciliation_section(report: GoldenEvaluationReport) -> list[str]:
        lines = ["## Reconciliation outcomes", ""]
        counts = report.reconciliation_outcome_counts
        if not counts:
            lines.extend(["_No cross-references produced._", ""])
            return lines
        for outcome, count in sorted(counts.items()):
            lines.append(f"- {outcome}: `{count}`")
        lines.append("")
        return lines

    @staticmethod
    def _render_not_evaluated_section(report: GoldenEvaluationReport) -> list[str]:
        not_evaluated = report.documents_not_evaluated
        lines = ["## Documents Not Evaluated", ""]
        if not not_evaluated:
            lines.extend(["_None._", ""])
            return lines
        for outcome in not_evaluated:
            lines.append(f"- `{outcome.alias}` -- {outcome.status.value}: {outcome.detail or ''}")
        lines.append("")
        return lines

    @staticmethod
    def _render_reproducibility_section(report: GoldenEvaluationReport) -> list[str]:
        metadata = report.run_metadata
        return [
            "## Reproducibility",
            "",
            f"- timestamp: `{metadata.timestamp}`",
            f"- git commit: `{metadata.git_commit or 'unknown'}`",
            f"- artifact schema version: `{metadata.artifact_schema_version}`",
            f"- parser: `{metadata.parser_name} {metadata.parser_version}`",
            f"- conversion fingerprint: `{metadata.conversion_fingerprint or 'unknown'}`",
            "",
        ]


__all__ = ["GoldenEvaluationReportMarkdownRenderer"]
