from src.application.evaluation import (
    RetrievalBenchmarkReportJsonSerializer,
)

from tests.unit.application.evaluation.retrieval.benchmarking.reporting.report_builders import (
    build_sample_report,
)


def test_json_serializer_emits_stable_shape_with_failure_diagnostics() -> None:
    report = build_sample_report()
    serializer = RetrievalBenchmarkReportJsonSerializer()

    payload = serializer.serialize(report)

    assert set(payload) == {
        "summary",
        "document_family_breakdown",
        "query_type_breakdown",
        "case_results",
    }
    assert payload["summary"]["case_count"] == 3
    assert len(payload["document_family_breakdown"]) == 3
    assert len(payload["query_type_breakdown"]) == 3

    first_case = payload["case_results"][0]
    failed_case = payload["case_results"][2]

    assert first_case["expected_document_family"] == "manual"
    assert first_case["anchor"]["chunks"][0]["retrieval_source"] == "sql"
    assert first_case["anchor"]["chunks"][0]["page_start"] == 1
    assert first_case["evaluation"]["meets_expected_rank_target"] is True

    assert failed_case["anchor"]["hit"] is False
    assert failed_case["context"]["hit"] is True
    assert failed_case["context"]["used_context_expansion"] is True
    assert failed_case["diagnostics"]["failure_reasons"] == [
        "Anchor retrieval did not return the expected evidence.",
        "Anchor retrieval did not return the resolved expected chunk id.",
        "Anchor retrieval missed the expected section path.",
        "Anchor retrieval did not return a chunk covering expected page 2.",
        "Context expansion recovered the expected evidence after the anchor miss.",
        "Context expansion reached the expected section path even though the anchor results did not.",
    ]
