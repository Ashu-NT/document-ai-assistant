from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path

from src.application.evaluation import (
    DEFAULT_RETRIEVAL_TRUTH_SET_PATH,
    RetrievalBenchmarkDataset,
    RetrievalBenchmarkResolutionFailureWriter,
)
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.shared.exceptions import ApplicationError, SchemaValidationError

_SUBSET_FULL = "full"
_SUBSET_IDENTIFIER = "identifier"
_SUBSET_SEMANTIC = "semantic"
_SUBSET_CHOICES = {_SUBSET_FULL, _SUBSET_IDENTIFIER, _SUBSET_SEMANTIC}


@dataclass(slots=True, kw_only=True)
class RunBenchmarkRequest(ToolRequest):
    truth_set_path: str | None = None
    manifest_path: str | None = None
    subset: str = _SUBSET_FULL
    output_directory: str | None = None


class RunBenchmarkTool:
    metadata = ToolMetadata(
        tool_name="run_benchmark",
        category="evaluation",
        description="Run the retrieval benchmark against the seeded corpus.",
        mutates_state=False,
    )

    def __init__(
        self,
        *,
        truth_set_loader,
        manifest_loader,
        dataset_resolver,
        evaluator,
        report_writer,
        workflow,
        evaluation_top_k: int,
        resolution_failure_writer: (
            RetrievalBenchmarkResolutionFailureWriter | None
        ) = None,
    ) -> None:
        self.truth_set_loader = truth_set_loader
        self.manifest_loader = manifest_loader
        self.dataset_resolver = dataset_resolver
        self.evaluator = evaluator
        self.report_writer = report_writer
        self.workflow = workflow
        self.evaluation_top_k = evaluation_top_k
        self.resolution_failure_writer = (
            resolution_failure_writer or RetrievalBenchmarkResolutionFailureWriter()
        )

    def run(self, request: RunBenchmarkRequest) -> ToolResult:
        if request.subset not in _SUBSET_CHOICES:
            return invalid_request_result(
                "subset must be one of: full, identifier, semantic.",
                metadata=self.metadata,
                diagnostics={"subset": request.subset},
            )

        manifest_path = Path(request.manifest_path or "")
        if not request.manifest_path or not manifest_path.exists():
            return ToolResult.fail(
                "Retrieval benchmark corpus manifest file not found.",
                error_code="benchmark_failed",
                diagnostics={
                    "manifest_path": str(manifest_path),
                    "suggested_seed_command": (
                        "python scripts/seed_retrieval_benchmark_corpus.py "
                        f"--truth-set {request.truth_set_path or DEFAULT_RETRIEVAL_TRUTH_SET_PATH}"
                    ),
                },
                metadata=self.metadata,
            )

        truth_set_path = Path(request.truth_set_path or DEFAULT_RETRIEVAL_TRUTH_SET_PATH)
        output_directory = Path(request.output_directory or "outputs/evaluation/retrieval")

        try:
            dataset = self.truth_set_loader.load(truth_set_path)
            selected_dataset = self._select_subset_dataset(dataset, request.subset)
            manifest = self.manifest_loader.load(manifest_path)
            resolved_dataset, skipped_case_ids = self._resolve_with_fallback(
                selected_dataset=selected_dataset,
                manifest=manifest,
                truth_set_path=truth_set_path,
                manifest_path=manifest_path,
                output_directory=output_directory,
                subset=request.subset,
            )
            report = self.evaluator.evaluate(self.workflow, resolved_dataset)
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        json_output_path, markdown_output_path = self._resolve_output_paths(
            output_directory=output_directory,
            subset=request.subset,
        )
        self.report_writer.write_json(report, json_output_path)
        self.report_writer.write_markdown(report, markdown_output_path)

        failed_case_count = sum(
            1
            for case_result in report.case_results
            if not case_result.meets_expected_rank_target
        )
        data = {
            "subset": request.subset,
            "selected_case_count": resolved_dataset.case_count,
            "failed_case_count": failed_case_count,
            "json_output_path": str(json_output_path),
            "markdown_output_path": str(markdown_output_path),
            "skipped_case_ids": sorted(skipped_case_ids),
            "report": report,
        }
        if failed_case_count == 0:
            return ToolResult.ok(data=data, metadata=self.metadata)

        return ToolResult.fail(
            "Retrieval benchmark completed with failed cases.",
            error_code="benchmark_failed",
            diagnostics=data,
            metadata=self.metadata,
            data=data,
        )

    def _select_subset_dataset(
        self,
        dataset: RetrievalBenchmarkDataset,
        subset: str,
    ) -> RetrievalBenchmarkDataset:
        if subset == _SUBSET_IDENTIFIER:
            selected_cases = dataset.identifier_focused_cases
        elif subset == _SUBSET_SEMANTIC:
            selected_cases = dataset.semantic_procedure_cases
        else:
            selected_cases = dataset.canonical_cases

        if not selected_cases:
            raise SchemaValidationError(
                "Retrieval benchmark subset did not contain any cases.",
                details={"subset": subset, "source_path": str(dataset.source_path)},
            )

        copied_cases = copy.deepcopy(selected_cases)
        for case in copied_cases:
            if case.query is not None:
                case.query.top_k = max(case.query.top_k, self.evaluation_top_k)

        return RetrievalBenchmarkDataset(
            source_path=dataset.source_path,
            cases=copied_cases,
            identifier_subset_definition=dataset.identifier_subset_definition,
            semantic_procedure_subset_definition=(
                dataset.semantic_procedure_subset_definition
            ),
        )

    def _resolve_with_fallback(
        self,
        *,
        selected_dataset: RetrievalBenchmarkDataset,
        manifest,
        truth_set_path: Path,
        manifest_path: Path,
        output_directory: Path,
        subset: str,
    ) -> tuple[RetrievalBenchmarkDataset, set[str]]:
        try:
            resolved = self.dataset_resolver.resolve_dataset(selected_dataset, manifest)
            return resolved, set()
        except SchemaValidationError as exc:
            details = exc.details or {}
            unresolved_case_ids = set(details.get("unresolved_case_ids") or [])
            if not unresolved_case_ids:
                raise

            self._write_resolution_failure_reports(
                details=details,
                truth_set_path=truth_set_path,
                manifest_path=manifest_path,
                output_directory=output_directory,
                subset=subset,
            )
            resolvable_cases = [
                case
                for case in selected_dataset.cases
                if case.case_id not in unresolved_case_ids
            ]
            if not resolvable_cases:
                raise
            partial_dataset = RetrievalBenchmarkDataset(
                source_path=selected_dataset.source_path,
                cases=resolvable_cases,
                identifier_subset_definition=(
                    selected_dataset.identifier_subset_definition
                ),
                semantic_procedure_subset_definition=(
                    selected_dataset.semantic_procedure_subset_definition
                ),
            )
            return self.dataset_resolver.resolve_dataset(
                partial_dataset,
                manifest,
            ), unresolved_case_ids

    def _write_resolution_failure_reports(
        self,
        *,
        details: dict,
        truth_set_path: Path,
        manifest_path: Path,
        output_directory: Path,
        subset: str,
    ) -> None:
        json_output_path, markdown_output_path = (
            self._resolve_resolution_warning_output_paths(
                output_directory=output_directory,
                subset=subset,
            )
        )
        self.resolution_failure_writer.write_json(
            details=details,
            output_path=json_output_path,
            subset=subset,
            truth_set_path=truth_set_path,
            manifest_path=manifest_path,
        )
        self.resolution_failure_writer.write_markdown(
            details=details,
            output_path=markdown_output_path,
            subset=subset,
            truth_set_path=truth_set_path,
            manifest_path=manifest_path,
        )

    @staticmethod
    def _resolve_output_paths(
        *,
        output_directory: Path,
        subset: str,
    ) -> tuple[Path, Path]:
        report_stem = (
            "retrieval_benchmark_report"
            if subset == _SUBSET_FULL
            else f"retrieval_benchmark_{subset}_report"
        )
        return (
            (output_directory / f"{report_stem}.json").resolve(),
            (output_directory / f"{report_stem}.md").resolve(),
        )

    def _resolve_resolution_warning_output_paths(
        self,
        *,
        output_directory: Path,
        subset: str,
    ) -> tuple[Path, Path]:
        json_output_path, markdown_output_path = self._resolve_output_paths(
            output_directory=output_directory,
            subset=subset,
        )
        return (
            json_output_path.with_name(
                f"{json_output_path.stem}_resolution_warning{json_output_path.suffix}"
            ),
            markdown_output_path.with_name(
                f"{markdown_output_path.stem}_resolution_warning{markdown_output_path.suffix}"
            ),
        )
