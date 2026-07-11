from tests.unit.application.evaluation.retrieval._test_run_retrieval_benchmark_support import *  # noqa: F401,F403

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
    assert "[retrieval-benchmark] Building benchmark runtime..." in stdout
    assert "[retrieval-benchmark] fake evaluator progress" in stdout
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

    json_report_path, markdown_report_path = resolve_resolution_warning_output_paths(
        output_directory=tmp_path / "reports",
        subset="full",
    )

    assert exit_code == 1
    assert json_report_path.exists()
    assert markdown_report_path.exists()
    assert "resolution_failed" in json_report_path.read_text(encoding="utf-8")
    assert "Retrieval Benchmark Resolution Failure" in markdown_report_path.read_text(
        encoding="utf-8"
    )

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

def test_close_runtime_closes_session_and_qdrant_client() -> None:
    session = FakeClosable()
    qdrant_client = FakeClosable()
    runtime = BenchmarkRuntime(
        truth_set_loader=FakeTruthSetLoader(build_dataset()),
        manifest_loader=FakeManifestLoader(build_manifest()),
        dataset_resolver=FakeDatasetResolver(),
        evaluator=FakeEvaluator(build_report(passing=True)),
        report_writer=FakeReportWriter(),
        workflow=object(),
        session=session,
        qdrant_client=qdrant_client,
    )

    close_runtime(runtime)

    assert session.close_calls == 1
    assert qdrant_client.close_calls == 1
