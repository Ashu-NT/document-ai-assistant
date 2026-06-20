from src.application.evaluation import (
    RetrievalBenchmarkReportSummaryBuilder,
)

from tests.unit.application.evaluation.retrieval.benchmarking.reporting.report_builders import (
    build_sample_report,
)


def test_summary_builder_groups_results_by_document_family_and_query_type() -> None:
    report = build_sample_report()
    summary_builder = RetrievalBenchmarkReportSummaryBuilder()

    overview = summary_builder.build_overview(report)
    family_rows = {
        row["label"]: row
        for row in summary_builder.build_document_family_breakdown(report)
    }
    query_rows = {
        row["label"]: row
        for row in summary_builder.build_query_type_breakdown(report)
    }

    assert overview["case_count"] == 3
    assert overview["hit_rate"] == 2 / 3
    assert overview["context_hit_rate"] == 1.0
    assert overview["rank_target_satisfaction_rate"] == 2 / 3

    assert family_rows["manual"]["case_count"] == 1
    assert family_rows["manual"]["hit_rate"] == 1.0
    assert family_rows["datasheet"]["case_count"] == 1
    assert family_rows["datasheet"]["hit_rate"] == 0.0
    assert family_rows["report"]["recall_at_3"] == 1.0

    assert query_rows["identifier_lookup"]["case_count"] == 1
    assert query_rows["identifier_lookup"]["rank_target_satisfaction_rate"] == 1.0
    assert query_rows["procedure_lookup"]["hit_rate"] == 1.0
    assert query_rows["safety_lookup"]["context_hit_rate"] == 1.0
