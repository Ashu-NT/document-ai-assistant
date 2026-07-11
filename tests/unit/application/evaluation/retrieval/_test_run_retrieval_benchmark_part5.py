import json

from dataclasses import dataclass

from pathlib import Path

from scripts.run_retrieval_benchmark import (
    BenchmarkRuntime,
    close_runtime,
    ensure_manifest_exists,
    main,
    resolve_resolution_warning_output_paths,
    select_subset_dataset,
)

from src.application.evaluation import (
    RetrievalBenchmarkCase,
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkCorpusDocument,
    RetrievalBenchmarkCorpusManifest,
    RetrievalBenchmarkDataset,
    RetrievalBenchmarkPriority,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkRankTarget,
    RetrievalBenchmarkReport,
)

from src.domain.retrieval import RetrievalQuery

from src.shared.exceptions import SchemaValidationError

def build_dataset() -> RetrievalBenchmarkDataset:
    return RetrievalBenchmarkDataset(
        source_path=Path("TestDoc/retrieval_truth_set.md"),
        cases=[
            RetrievalBenchmarkCase(
                case_id="ID-001",
                query=RetrievalQuery(
                    query_id="ID-001",
                    query_text="What is the drawing number?",
                ),
                query_type=RetrievalBenchmarkQueryType.IDENTIFIER_LOOKUP,
                expected_document_alias="drawing_nav_lights_13759_3540",
                expected_file_name="drawing.pdf",
                expected_section_path_text="Title Block",
                expected_page=1,
                expected_relevant_passage="Drawing number 13759_3540_01.00",
                priority=RetrievalBenchmarkPriority.HIGH,
                expected_rank_target=RetrievalBenchmarkRankTarget.TOP_3,
            ),
            RetrievalBenchmarkCase(
                case_id="SEM-001",
                query=RetrievalQuery(
                    query_id="SEM-001",
                    query_text="How do I commission the device?",
                ),
                query_type=RetrievalBenchmarkQueryType.PROCEDURE_LOOKUP,
                expected_document_alias="report_pressure_transmitter",
                expected_file_name="report.pdf",
                expected_section_path_text="Operating Instructions > Commissioning",
                expected_page=7,
                expected_relevant_passage="Commission the device in safe conditions.",
                priority=RetrievalBenchmarkPriority.MEDIUM,
                expected_rank_target=RetrievalBenchmarkRankTarget.TOP_5,
            ),
        ],
    )

def build_manifest() -> RetrievalBenchmarkCorpusManifest:
    return RetrievalBenchmarkCorpusManifest(
        truth_set_path=Path("TestDoc/retrieval_truth_set.md"),
        input_directory=Path("TestDoc"),
        generated_at="2026-06-20T00:00:00+00:00",
        documents=[
            RetrievalBenchmarkCorpusDocument(
                document_alias="drawing_nav_lights_13759_3540",
                document_id="doc_drawing",
                file_name="drawing.pdf",
                file_path=Path("TestDoc/drawing.pdf"),
                file_hash="file_hash_1",
                content_hash="content_hash_1",
                document_type="drawing",
                page_count=1,
                section_count=1,
                element_count=2,
                chunk_count=1,
                question_count=0,
            ),
            RetrievalBenchmarkCorpusDocument(
                document_alias="report_pressure_transmitter",
                document_id="doc_report",
                file_name="report.pdf",
                file_path=Path("TestDoc/report.pdf"),
                file_hash="file_hash_2",
                content_hash="content_hash_2",
                document_type="report",
                page_count=10,
                section_count=4,
                element_count=9,
                chunk_count=6,
                question_count=5,
            ),
        ],
    )

class FakeTruthSetLoader:
    def __init__(self, dataset: RetrievalBenchmarkDataset) -> None:
        self.dataset = dataset
        self.calls: list[Path | str | None] = []

    def load(self, path):
        self.calls.append(path)
        return self.dataset

class FakeManifestLoader:
    def __init__(self, manifest: RetrievalBenchmarkCorpusManifest) -> None:
        self.manifest = manifest
        self.calls: list[Path | str] = []

    def load(self, path):
        self.calls.append(path)
        return self.manifest

class FakeDatasetResolver:
    def __init__(self) -> None:
        self.calls: list[tuple[RetrievalBenchmarkDataset, RetrievalBenchmarkCorpusManifest]] = []
        self.error: Exception | None = None

    def resolve_dataset(self, dataset, manifest):
        if self.error is not None:
            raise self.error
        self.calls.append((dataset, manifest))
        return dataset

class FakePartialFailureDatasetResolver:
    def __init__(self, unresolved_case_ids: list[str]) -> None:
        self.unresolved_case_ids = unresolved_case_ids
        self.calls: list[list[str]] = []

    def resolve_dataset(self, dataset, manifest):
        case_ids = [case.case_id for case in dataset.cases]
        self.calls.append(case_ids)
        if len(self.calls) == 1:
            raise SchemaValidationError(
                "Resolution failed.",
                details={
                    "unresolved_case_ids": list(self.unresolved_case_ids),
                    "diagnostics": [
                        {
                            "case_id": case_id,
                            "message": "No final chunk matched the expected section/page/passage signals.",
                        }
                        for case_id in self.unresolved_case_ids
                    ],
                },
            )
        return dataset

class FakeEvaluator:
    def __init__(self, report: RetrievalBenchmarkReport) -> None:
        self.report = report
        self.calls: list[list[str]] = []

    def evaluate(self, workflow, benchmark_cases, progress_callback=None):
        self.calls.append([case.case_id for case in benchmark_cases.cases])
        if progress_callback is not None:
            progress_callback("fake evaluator progress")
        return self.report

class FakeReportWriter:
    def __init__(self) -> None:
        self.json_paths: list[Path] = []
        self.markdown_paths: list[Path] = []

    def write_json(self, report, output_path):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"case_count": report.case_count}), encoding="utf-8")
        self.json_paths.append(path)
        return path

    def write_markdown(self, report, output_path):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Report\n\nCases: {report.case_count}\n", encoding="utf-8")
        self.markdown_paths.append(path)
        return path

class FakeClosable:
    def __init__(self) -> None:
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1

class FakeRuntimeBuilder:
    runtime: BenchmarkRuntime

    def __call__(self) -> BenchmarkRuntime:
        return self.runtime

def build_report(*, passing: bool) -> RetrievalBenchmarkReport:
    benchmark_case = RetrievalBenchmarkCase(
        case_id="ID-001",
        query=RetrievalQuery(
            query_id="ID-001",
            query_text="What is the drawing number?",
        ),
        query_type=RetrievalBenchmarkQueryType.IDENTIFIER_LOOKUP,
        expected_document_alias="drawing_nav_lights_13759_3540",
        expected_file_name="drawing.pdf",
        expected_rank_target=RetrievalBenchmarkRankTarget.TOP_3,
    )
    case_result = RetrievalBenchmarkCaseResult(
        case=benchmark_case,
        hit=passing,
        matched_rank=1 if passing else None,
        reciprocal_rank=1.0 if passing else 0.0,
    )
    return RetrievalBenchmarkReport(case_results=[case_result])

def test_main_preserves_resolution_warning_report_when_partial_resolution_succeeds(
    monkeypatch,
    tmp_path: Path,
) -> None:
    partial_resolver = FakePartialFailureDatasetResolver(["SEM-001"])
    runtime = BenchmarkRuntime(
        truth_set_loader=FakeTruthSetLoader(build_dataset()),
        manifest_loader=FakeManifestLoader(build_manifest()),
        dataset_resolver=partial_resolver,
        evaluator=FakeEvaluator(build_report(passing=True)),
        report_writer=FakeReportWriter(),
        workflow=object(),
        session=None,
    )

    monkeypatch.setattr(
        "scripts.run_retrieval_benchmark.build_benchmark_runtime",
        FakeRuntimeBuilder(runtime),
    )
    monkeypatch.setattr(
        "scripts.run_retrieval_benchmark.benchmark_evaluation_top_k",
        lambda: 10,
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")

    exit_code = main(
        [
            "--manifest",
            str(manifest_path),
            "--output-dir",
            str(tmp_path / "reports"),
        ]
    )

    final_json_path = tmp_path / "reports" / "retrieval_benchmark_report.json"
    warning_json_path, warning_markdown_path = resolve_resolution_warning_output_paths(
        output_directory=tmp_path / "reports",
        subset="full",
    )

    assert exit_code == 0
    assert partial_resolver.calls == [["ID-001", "SEM-001"], ["ID-001"]]
    assert final_json_path.exists()
    assert warning_json_path.exists()
    assert warning_markdown_path.exists()
    assert "resolution_failed" in warning_json_path.read_text(encoding="utf-8")
    assert json.loads(final_json_path.read_text(encoding="utf-8"))["case_count"] == 1

def test_ensure_manifest_exists_raises_friendly_seed_guidance(
    tmp_path: Path,
) -> None:
    missing_manifest = tmp_path / "missing_manifest.json"

    try:
        ensure_manifest_exists(
            manifest_path=missing_manifest,
            truth_set_argument="TestDoc/retrieval_truth_set.md",
        )
    except SchemaValidationError as exc:
        assert (
            exc.message
            == "Retrieval benchmark corpus manifest file not found. "
            "Seed the retrieval benchmark corpus first, or pass --manifest to an "
            "existing benchmark corpus manifest."
        )
        assert exc.details is not None
        assert exc.details["path"] == str(missing_manifest)
        assert exc.details["suggested_seed_command"] == (
            "python scripts/seed_retrieval_benchmark_corpus.py "
            "--truth-set TestDoc/retrieval_truth_set.md"
        )
    else:
        raise AssertionError("Expected SchemaValidationError for missing manifest.")
