from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_golden_metrics import (
    aggregate_extraction_metrics,
    build_bucket_keyed_results,
    collect_applicability_counts,
    summarize_buckets_by,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
)
from src.application.evaluation.golden.golden_evaluation_report import (
    GoldenEvaluationReport,
)


def _format_ratio(value: float | None) -> str:
    # An explicit "n/a" rather than 0.00 - a metric with no denominator is
    # not the same as a metric that scored zero.
    return f"{value:.2f}" if value is not None else "n/a"


def _format_optional_bool(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "yes" if value else "no"


class GoldenEvaluationReportMarkdownRenderer:
    def render(self, report: GoldenEvaluationReport) -> str:
        lines: list[str] = ["# Golden Evaluation", ""]

        lines.extend(self._render_corpus_section(report))
        lines.extend(self._render_structural_section(report))
        lines.extend(self._render_chunking_section(report))
        lines.extend(self._render_cross_reference_section(report))
        lines.extend(self._render_reconciliation_section(report))
        lines.extend(self._render_classification_section(report))
        lines.extend(self._render_extraction_section(report))
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
        lines = [
            "## Structural",
            "",
            f"- passed documents: `{report.structural_passed_count}`",
            f"- failed documents: `{report.structural_failed_count}`",
            f"- structural assertion failures: `{report.structural_assertion_failure_count}`",
            "",
        ]
        lines.extend(
            GoldenEvaluationReportMarkdownRenderer._render_baseline_provenance(report)
        )
        return lines

    @staticmethod
    def _render_baseline_provenance(report: GoldenEvaluationReport) -> list[str]:
        """Diagnostic only - never a pass/fail signal. A baseline recorded
        under a different parser/version than the current run is reported
        so a human can decide whether to re-review it, never automatically
        invalidated (see StructuralBaselineProvenance)."""
        recorded = [
            (outcome.alias, outcome.structural_result.provenance)
            for outcome in report.document_outcomes
            if outcome.structural_result is not None
            and outcome.structural_result.provenance is not None
            and outcome.structural_result.provenance.is_recorded
        ]
        if not recorded:
            return []

        run_metadata = report.run_metadata
        lines = ["### Baseline provenance (diagnostic only)", ""]
        for alias, provenance in recorded:
            matches = (
                provenance.parser_version == run_metadata.parser_version
                and provenance.conversion_fingerprint
                == run_metadata.conversion_fingerprint
            )
            status = "matches current run" if matches else "differs from current run"
            lines.append(
                f"- `{alias}`: recorded `{provenance.parser_name} "
                f"{provenance.parser_version}` (fingerprint "
                f"`{provenance.conversion_fingerprint or 'unknown'}`) - {status}"
            )
        lines.append("")
        return lines

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
    def _render_classification_section(report: GoldenEvaluationReport) -> list[str]:
        lines = ["## Classification", ""]
        results = report.classification_results
        if not results:
            lines.extend(["_Classification was not evaluated in this run._", ""])
            return lines

        metrics = report.classification_metrics
        lines.extend(
            [
                "### Execution",
                "",
                f"- documents classified: `{metrics.executed_count}`",
                f"- execution failures: `{metrics.execution_failed_count}`",
                "- skipped (no parsed document available): "
                f"`{metrics.skipped_parsing_unavailable_count}`",
                "",
                "### Accuracy (REVIEWED, non-ambiguous golden labels only)",
                "",
                "- reviewed eligible documents (denominator): "
                f"`{metrics.reviewed_eligible_document_count}`",
            ]
        )
        if metrics.reviewed_eligible_document_count == 0:
            lines.append(
                "- _No golden classification label has been human-reviewed yet, so "
                "there is no authoritative accuracy to report. Candidate labels are "
                "shown per-document below but are deliberately NOT scored as truth._"
            )
        else:
            lines.extend(
                [
                    f"- raw predictions correct: `{metrics.raw_correct_count}`",
                    f"- raw accuracy: `{_format_ratio(metrics.raw_accuracy)}`",
                    "- accepted (passed confidence gate): "
                    f"`{metrics.accepted_count}`",
                    f"- accepted and correct: `{metrics.accepted_correct_count}`",
                    "- accepted classification accuracy "
                    "(accepted_correct / reviewed_eligible): "
                    f"`{_format_ratio(metrics.accepted_classification_accuracy)}`",
                    "- accuracy among accepted (accepted_correct / accepted): "
                    f"`{_format_ratio(metrics.accuracy_among_accepted)}`",
                ]
            )
        lines.append("")

        lines.extend(
            [
                "### Model behaviour (all classified documents)",
                "",
                f"- UNKNOWN predictions: `{metrics.unknown_count}`",
                f"- UNKNOWN rate: `{_format_ratio(metrics.unknown_rate)}`",
                "- rejected by confidence gate: "
                f"`{metrics.low_confidence_rejected_count}`",
                "- low-confidence rejection rate: "
                f"`{_format_ratio(metrics.low_confidence_rejection_rate)}`",
                f"- confidence scores observed: `{metrics.confidence_count}`",
                f"- confidence min: `{_format_ratio(metrics.confidence_min)}`",
                f"- confidence max: `{_format_ratio(metrics.confidence_max)}`",
                f"- confidence mean: `{_format_ratio(metrics.confidence_mean)}`",
                f"- confidence median: `{_format_ratio(metrics.confidence_median)}`",
                "",
            ]
        )

        lines.extend(
            GoldenEvaluationReportMarkdownRenderer._render_confusion_matrix(metrics)
        )

        lines.extend(
            [
                "### Ambiguous documents (reported separately, never in the "
                "accuracy denominator)",
                "",
                f"- ambiguous documents classified: `{metrics.ambiguous_document_count}`",
                "- ambiguous documents whose raw prediction matched the (debatable) "
                f"expected label: `{metrics.ambiguous_raw_match_count}`",
                "",
            ]
        )

        lines.extend(
            [
                "### Per-document results",
                "",
                "| alias | expected | review | ambiguous | predicted | confidence | "
                "gate | raw correct | accepted correct | status |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for result in results:
            expectation = result.expectation
            attempt = result.attempt
            lines.append(
                "| {alias} | {expected} | {review} | {ambiguous} | {predicted} | "
                "{confidence} | {gate} | {raw} | {accepted} | {status} |".format(
                    alias=result.alias,
                    expected=(
                        expectation.expected_document_type.value
                        if expectation is not None
                        else "n/a (no golden label)"
                    ),
                    review=(
                        expectation.review_status.value
                        if expectation is not None
                        else "n/a"
                    ),
                    ambiguous=(
                        "yes" if expectation is not None and expectation.ambiguous else "no"
                    ),
                    predicted=(
                        attempt.predicted_document_type.value
                        if attempt is not None
                        else "n/a"
                    ),
                    confidence=(
                        _format_ratio(attempt.confidence) if attempt is not None else "n/a"
                    ),
                    gate=(
                        ("passed" if attempt.passed_confidence_gate else "rejected")
                        if attempt is not None
                        else "n/a"
                    ),
                    raw=_format_optional_bool(result.raw_prediction_correct),
                    accepted=_format_optional_bool(result.accepted_classification_correct),
                    status=result.stage_status.value,
                )
            )
        lines.append("")
        return lines

    @staticmethod
    def _render_confusion_matrix(metrics) -> list[str]:
        lines = ["### Confusion matrix (expected rows x predicted columns)", ""]
        matrix = metrics.confusion_matrix
        if not matrix:
            lines.extend(
                [
                    "_No reviewed, non-ambiguous golden label with a successful "
                    "classification attempt - nothing to tabulate._",
                    "",
                ]
            )
            return lines

        predicted_labels = sorted(
            {predicted for row in matrix.values() for predicted in row}
        )
        lines.append("| expected \\ predicted | " + " | ".join(predicted_labels) + " |")
        lines.append("| --- |" + " --- |" * len(predicted_labels))
        for expected_label in sorted(matrix):
            row = matrix[expected_label]
            counts = " | ".join(str(row.get(p, 0)) for p in predicted_labels)
            lines.append(f"| {expected_label} | {counts} |")
        lines.append("")
        return lines

    @staticmethod
    def _render_extraction_section(report: GoldenEvaluationReport) -> list[str]:
        lines = ["## Extraction (Phase 2B)", ""]
        results = report.extraction_results
        if not results:
            lines.extend(["_Extraction was not evaluated in this run._", ""])
            return lines

        lines.extend(
            [
                "_CANDIDATE metrics below are NON-AUTHORITATIVE until a human "
                "reviews the underlying expectations (review_status: reviewed). "
                "REVIEWED tables are the authoritative baseline once any exist._",
                "",
            ]
        )

        lines.extend(GoldenEvaluationReportMarkdownRenderer._render_extraction_execution(results))
        lines.extend(
            GoldenEvaluationReportMarkdownRenderer._render_extraction_applicability(results)
        )
        for review_status in (ExtractionReviewStatus.REVIEWED, ExtractionReviewStatus.CANDIDATE):
            lines.extend(
                GoldenEvaluationReportMarkdownRenderer._render_extraction_metrics_table(
                    results, review_status=review_status
                )
            )
        lines.extend(
            GoldenEvaluationReportMarkdownRenderer._render_extraction_mismatches(results)
        )
        return lines

    @staticmethod
    def _render_extraction_execution(results: list) -> list[str]:
        evaluated = sum(1 for r in results if r.was_evaluated)
        execution_failed = sum(1 for r in results if r.has_execution_failures)
        scope_count = sum(len(r.scope_outcomes) for r in results)
        return [
            "### Execution",
            "",
            f"- documents with an extraction expectation: `{len(results)}`",
            f"- documents evaluated (at least one scope ran): `{evaluated}`",
            f"- documents with an execution failure in at least one scope: "
            f"`{execution_failed}`",
            f"- (document, scope) executions: `{scope_count}`",
            "",
        ]

    @staticmethod
    def _render_extraction_applicability(results: list) -> list[str]:
        counts = collect_applicability_counts(results)
        return [
            "### Applicability",
            "",
            f"- APPLICABLE: `{counts.applicable}`",
            f"- NOT_APPLICABLE: `{counts.not_applicable}`",
            f"- NOT_ASSESSED (explicit declarations only - absence of any "
            f"declaration is never counted here): `{counts.not_assessed}`",
            "",
        ]

    @staticmethod
    def _render_extraction_metrics_table(
        results: list, *, review_status: ExtractionReviewStatus
    ) -> list[str]:
        keyed = build_bucket_keyed_results(results)
        buckets = aggregate_extraction_metrics(keyed)
        rolled = summarize_buckets_by(buckets, only_review_status=review_status)

        label = "REVIEWED (authoritative)" if review_status.value == "reviewed" else "CANDIDATE (non-authoritative)"
        lines = [f"### Metrics - {label}", ""]
        if not rolled:
            lines.extend([f"_No {review_status.value} expectations evaluated._", ""])
            return lines

        lines.append(
            "| entity_type | completeness | TP | FP | FN | precision | recall | f1 | "
            "evidence correct | evidence incorrect | ambiguous |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for (entity_type, completeness), bucket in sorted(rolled.items()):
            fp = (
                str(bucket.false_positive_count)
                if completeness is ExtractionCompleteness.EXHAUSTIVE
                else "n/a (presence-only)"
            )
            lines.append(
                f"| {entity_type} | {completeness.value} | "
                f"{bucket.true_positive_count} | {fp} | {bucket.false_negative_count} | "
                f"{_format_ratio(bucket.precision)} | {_format_ratio(bucket.recall)} | "
                f"{_format_ratio(bucket.f1)} | {bucket.evidence_correct_count} | "
                f"{bucket.evidence_incorrect_count} | {bucket.ambiguous_count} |"
            )
        lines.append("")
        return lines

    @staticmethod
    def _render_extraction_mismatches(results: list) -> list[str]:
        lines = ["### Mismatches (diagnostic detail)", ""]
        any_mismatch = False
        for document_result in results:
            for scope_outcome in document_result.scope_outcomes:
                if scope_outcome.stage_status.value == "execution_failed":
                    any_mismatch = True
                    lines.append(
                        f"- `{document_result.alias}` scope "
                        f"`{scope_outcome.scope.scope_type.value} "
                        f"{scope_outcome.scope.page_start}-{scope_outcome.scope.page_end}`: "
                        f"EXECUTION_FAILED - {scope_outcome.execution_error}"
                    )
                    continue
                for match in scope_outcome.match_results:
                    if match.outcome is ExtractionMatchOutcome.MATCHED and match.evidence_correct is not False and not match.differing_fields:
                        continue
                    any_mismatch = True
                    detail_parts = [f"outcome={match.outcome.value}"]
                    if match.expectation is not None:
                        detail_parts.append(f"case_id={match.expectation.case_id}")
                    if match.differing_fields:
                        detail_parts.append(f"differing_fields={list(match.differing_fields)}")
                    if match.ambiguous_actual_entity_ids:
                        detail_parts.append(
                            f"ambiguous_candidates={list(match.ambiguous_actual_entity_ids)}"
                        )
                    if match.evidence_correct is False:
                        detail_parts.append(f"evidence_incorrect={match.evidence_detail}")
                    detail_parts.append(f"reason={match.match_reason}")
                    lines.append(
                        f"- `{document_result.alias}` / `{match.entity_type}`: "
                        + "; ".join(detail_parts)
                    )
        if not any_mismatch:
            lines.append("_No mismatches - every evaluated expectation matched cleanly._")
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
        lines = [
            "## Reproducibility",
            "",
            f"- timestamp: `{metadata.timestamp}`",
            f"- git commit: `{metadata.git_commit or 'unknown'}`",
            f"- artifact schema version: `{metadata.artifact_schema_version}`",
            f"- parser: `{metadata.parser_name} {metadata.parser_version}`",
            f"- conversion fingerprint: `{metadata.conversion_fingerprint or 'unknown'}`",
        ]
        if metadata.classification_execution_mode is not None:
            lines.extend(
                [
                    "- classification execution mode: "
                    f"`{metadata.classification_execution_mode}`",
                    f"- classification model: `{metadata.classification_model or 'unknown'}`",
                    "- classification prompt version: "
                    f"`{metadata.classification_prompt_version or 'unknown'}`",
                    "- classification confidence threshold: "
                    f"`{metadata.classification_confidence_threshold}`",
                    "- production setting allow_reclassification (recorded, NOT used "
                    f"by this run): `{metadata.classification_allow_reclassification}`",
                    "- production setting use_cache (recorded, NOT used by this run): "
                    f"`{metadata.classification_use_cache}`",
                ]
            )
        if metadata.extraction_execution_mode is not None or metadata.extraction_model is not None:
            lines.extend(
                [
                    f"- extraction execution mode: `{metadata.extraction_execution_mode}`",
                    f"- extraction model: `{metadata.extraction_model or 'unknown'}`",
                    "- extraction prompt version: "
                    f"`{metadata.extraction_prompt_version or 'unknown'}`",
                    f"- extraction temperature: `{metadata.extraction_temperature}`",
                    f"- extraction max attempts: `{metadata.extraction_max_attempts}`",
                    "- extraction allow_partial_batches: "
                    f"`{metadata.extraction_allow_partial_batches}`",
                    "- extraction candidate_narrowing_enabled: "
                    f"`{metadata.extraction_candidate_narrowing_enabled}`",
                    "- extraction confidence threshold (flags requires_human_review "
                    "only - never drops an entity): "
                    f"`{metadata.extraction_confidence_threshold}`",
                ]
            )
        lines.append("")
        return lines


__all__ = ["GoldenEvaluationReportMarkdownRenderer"]
