import json
from dataclasses import dataclass
from pathlib import Path

from scripts.run_retrieval_benchmark import (
    BenchmarkRuntime,
    ensure_manifest_exists,
    main,
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


class FakeEvaluator:
    def __init__(self, report: RetrievalBenchmarkReport) -> None:
        self.report = report
        self.calls: list[list[str]] = []

    def evaluate(self, workflow, benchmark_cases):
        self.calls.append([case.case_id for case in benchmark_cases.cases])
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


@dataclass(slots=True)
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


def test_select_subset_dataset_filters_cases_and_lifts_top_k() -> None:
    dataset = build_dataset()

    identifier_dataset = select_subset_dataset(
        dataset,
        subset="identifier",
        evaluation_top_k=10,
    )
    semantic_dataset = select_subset_dataset(
        dataset,
        subset="semantic",
        evaluation_top_k=10,
    )

    assert [case.case_id for case in identifier_dataset.cases] == ["ID-001"]
    assert [case.case_id for case in semantic_dataset.cases] == ["SEM-001"]
    assert identifier_dataset.cases[0].query is not None
    assert semantic_dataset.cases[0].query is not None
    assert identifier_dataset.cases[0].query.top_k == 10
    assert semantic_dataset.cases[0].query.top_k == 10


def test_main_uses_cli_path_override_and_subset_selection(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    dataset = build_dataset()
    manifest = build_manifest()
    truth_loader = FakeTruthSetLoader(dataset)
    manifest_loader = FakeManifestLoader(manifest)
    dataset_resolver = FakeDatasetResolver()
    evaluator = FakeEvaluator(build_report(passing=True))
    report_writer = FakeReportWriter()
    runtime = BenchmarkRuntime(
        truth_set_loader=truth_loader,
        manifest_loader=manifest_loader,
        dataset_resolver=dataset_resolver,
        evaluator=evaluator,
        report_writer=report_writer,
        workflow=object(),
        session=None,
    )
    truth_set_path = tmp_path / "custom_truth.md"
    manifest_path = tmp_path / "custom_manifest.json"
    truth_set_path.write_text("truth-set", encoding="utf-8")
    manifest_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.run_retrieval_benchmark.build_benchmark_runtime",
        FakeRuntimeBuilder(runtime),
    )
    monkeypatch.setattr(
        "scripts.run_retrieval_benchmark.benchmark_evaluation_top_k",
        lambda: 10,
    )

    exit_code = main(
        [
            "--truth-set",
            str(truth_set_path),
            "--manifest",
            str(manifest_path),
            "--subset",
            "identifier",
            "--output-dir",
            str(tmp_path / "reports"),
        ]
    )

    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert truth_loader.calls == [truth_set_path.resolve()]
    assert manifest_loader.calls == [manifest_path.resolve()]
    assert evaluator.calls == [["ID-001"]]
    assert "subset: identifier" in stdout
    assert report_writer.json_paths[0].name == "retrieval_benchmark_identifier_report.json"
    assert report_writer.markdown_paths[0].name == "retrieval_benchmark_identifier_report.md"


def test_main_returns_non_zero_for_failed_benchmark(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runtime = BenchmarkRuntime(
        truth_set_loader=FakeTruthSetLoader(build_dataset()),
        manifest_loader=FakeManifestLoader(build_manifest()),
        dataset_resolver=FakeDatasetResolver(),
        evaluator=FakeEvaluator(build_report(passing=False)),
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

    assert exit_code == 2


def test_main_returns_non_zero_for_unresolved_truth_cases(
    monkeypatch,
    tmp_path: Path,
) -> None:
    dataset_resolver = FakeDatasetResolver()
    dataset_resolver.error = SchemaValidationError(
        "Resolution failed.",
        details={"unresolved_case_ids": ["ID-001"]},
    )
    runtime = BenchmarkRuntime(
        truth_set_loader=FakeTruthSetLoader(build_dataset()),
        manifest_loader=FakeManifestLoader(build_manifest()),
        dataset_resolver=dataset_resolver,
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

    assert exit_code == 1


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
