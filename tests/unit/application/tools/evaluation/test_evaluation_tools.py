from pathlib import Path

from src.application.evaluation.retrieval import (
    RetrievalBenchmarkCase,
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkDataset,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkReport,
)
from src.application.tools.evaluation import (
    RunBenchmarkRequest,
    RunBenchmarkTool,
    RunQualityGateRequest,
    RunQualityGateTool,
)


class FakeTruthSetLoader:
    def load(self, path):
        return RetrievalBenchmarkDataset(
            source_path=Path(path),
            cases=[
                RetrievalBenchmarkCase(
                    case_id="case-1",
                    query_text="serial number",
                    query_type=RetrievalBenchmarkQueryType.IDENTIFIER_LOOKUP,
                )
            ],
        )


class FakeManifestLoader:
    def load(self, path):
        return object()


class FakeDatasetResolver:
    def resolve_dataset(self, dataset, manifest):
        return dataset


class FakeEvaluator:
    def evaluate(self, workflow, dataset):
        return RetrievalBenchmarkReport(
            case_results=[
                RetrievalBenchmarkCaseResult(
                    case=dataset.cases[0],
                    hit=True,
                    matched_rank=1,
                    reciprocal_rank=1.0,
                )
            ]
        )


class FakeReportWriter:
    def __init__(self) -> None:
        self.json_paths = []
        self.markdown_paths = []

    def write_json(self, report, output_path):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
        self.json_paths.append(path)
        return path

    def write_markdown(self, report, output_path):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# report", encoding="utf-8")
        self.markdown_paths.append(path)
        return path


def test_run_quality_gate_tool_returns_failure_for_threshold_violation():
    tool = RunQualityGateTool()

    result = tool.run(
        RunQualityGateRequest(
            report_data={
                "summary": {
                    "hit_rate": 0.1,
                    "mean_reciprocal_rank": 0.1,
                    "recall_at_5": 0.1,
                    "context_hit_rate": 0.1,
                    "identifier_top_1_accuracy": 0.1,
                }
            }
        )
    )

    assert result.success is False
    assert result.error_code == "quality_gate_failed"
    assert "summary" in result.data


def test_run_benchmark_tool_delegates_to_runner_components(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    output_dir = tmp_path / "reports"
    writer = FakeReportWriter()
    tool = RunBenchmarkTool(
        truth_set_loader=FakeTruthSetLoader(),
        manifest_loader=FakeManifestLoader(),
        dataset_resolver=FakeDatasetResolver(),
        evaluator=FakeEvaluator(),
        report_writer=writer,
        workflow=object(),
        evaluation_top_k=10,
    )

    result = tool.run(
        RunBenchmarkRequest(
            truth_set_path=str(tmp_path / "truth.md"),
            manifest_path=str(manifest_path),
            output_directory=str(output_dir),
        )
    )

    assert result.success is True
    assert result.data["selected_case_count"] == 1
    assert writer.json_paths[0].exists()
    assert writer.markdown_paths[0].exists()
