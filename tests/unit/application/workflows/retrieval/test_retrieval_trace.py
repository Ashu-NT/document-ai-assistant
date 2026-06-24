import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.application.workflows.retrieval.tracing.retrieval_trace import (
    RetrievalTrace,
    TracedQueryAnalysis,
)
from src.application.workflows.retrieval.tracing.retrieval_trace_recorder import (
    RetrievalTraceRecorder,
)
from src.application.workflows.retrieval.tracing.retrieval_trace_writer import (
    RetrievalTraceWriter,
)


def _make_query(text="How do I change the oil?"):
    from src.domain.common import new_id
    from src.domain.retrieval import RetrievalQuery

    return RetrievalQuery(
        query_id=new_id("q"),
        query_text=text,
        top_k=5,
    )


def _make_retrieved_chunk(chunk_id="c1", score=0.85):
    mock = MagicMock()
    mock.chunk_id = chunk_id
    mock.document_id = "doc1"
    mock.chunk_type.value = "maintenance_procedure"
    mock.score = score
    mock.section_path = ["Chapter 1", "Maintenance"]
    mock.source.page_start = 10
    mock.source.page_end = 12
    mock.metadata = {
        "fused_score": 0.9,
        "best_source_score": 0.88,
        "retrieval_sources": ["dense", "keyword"],
        "dedup_reason": None,
        "dedup_collapsed_chunk_ids": [],
        "dedup_group_size": None,
        "dedup_representative_selection_reason": None,
    }
    mock.content = "Change oil every 500 hours."
    return mock


class TestRetrievalTraceRecorder:
    def test_build_returns_trace_with_all_fields(self):
        recorder = RetrievalTraceRecorder()
        query = _make_query()

        recorder.record_query_analysis(query)
        recorder.record_candidates([_make_retrieved_chunk("c1"), _make_retrieved_chunk("c2")])
        recorder.record_dedup(
            before_count=2,
            after_chunks=[_make_retrieved_chunk("c1")],
        )
        recorder.record_context_expansion([_make_retrieved_chunk("c1")])

        trace = recorder.build(query_id=query.query_id, timestamp_iso="2026-01-01T00:00:00")

        assert isinstance(trace, RetrievalTrace)
        assert trace.query_id == query.query_id
        assert trace.candidate_count == 2
        assert trace.dedup_removed_count == 1
        assert trace.final_chunk_count == 1
        assert trace.context_chunk_count == 1
        assert trace.context_chunk_ids == ["c1"]
        assert trace.duration_ms >= 0

    def test_query_analysis_captures_intent(self):
        recorder = RetrievalTraceRecorder()
        query = _make_query("What is the oil change interval?")
        recorder.record_query_analysis(query)
        trace = recorder.build(query_id=query.query_id, timestamp_iso="2026-01-01T00:00:00")
        assert trace.query_analysis.raw_query == "What is the oil change interval?"
        assert trace.query_analysis.detected_intent != ""

    def test_build_without_any_recordings(self):
        recorder = RetrievalTraceRecorder()
        trace = recorder.build(query_id="q1", timestamp_iso="2026-01-01T00:00:00")
        assert trace.candidate_count == 0
        assert trace.retrieved_chunks == []
        assert trace.pre_guardrail is None
        assert trace.post_guardrail is None

    def test_guardrail_recorded(self):
        recorder = RetrievalTraceRecorder()
        mock_result = MagicMock()
        mock_result.allowed = False
        mock_result.decision = MagicMock()
        mock_result.decision.__str__ = lambda _: "BLOCKED"
        mock_result.safe_user_message = "Query blocked."

        recorder.record_pre_guardrail(mock_result)
        trace = recorder.build(query_id="q1", timestamp_iso="2026-01-01T00:00:00")

        assert trace.pre_guardrail is not None
        assert not trace.pre_guardrail.allowed
        assert trace.pre_guardrail.phase == "pre_retrieval"


class TestRetrievalTraceWriter:
    def test_write_creates_json_file(self, tmp_path):
        recorder = RetrievalTraceRecorder()
        trace = recorder.build(query_id="q_test", timestamp_iso="2026-01-01T00:00:00")

        writer = RetrievalTraceWriter(output_dir=tmp_path)
        path = writer.write(trace)

        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["query_id"] == "q_test"
        assert "timestamp_iso" in data
        assert "duration_ms" in data

    def test_write_filename_contains_query_id(self, tmp_path):
        recorder = RetrievalTraceRecorder()
        trace = recorder.build(query_id="myquery123", timestamp_iso="2026-06-15T10:30:00")
        writer = RetrievalTraceWriter(output_dir=tmp_path)
        path = writer.write(trace)
        assert "myquery123" in path.name


class TestRetrievalWorkflowTracing:
    def test_run_accepts_trace_recorder_param(self):
        from src.application.validation.retrieval import RetrievalQueryValidator
        from src.application.workflows.retrieval import RetrievalWorkflow
        from src.domain.common import new_id
        from src.domain.retrieval import RetrievalQuery, RetrievalResult

        fake_result = RetrievalResult(
            result_id=new_id("r"),
            query=RetrievalQuery(query_id=new_id("q"), query_text="test", top_k=5),
            chunks=[],
            citations=[],
        )
        fake_service = MagicMock()
        fake_service.retrieve.return_value = fake_result

        workflow = RetrievalWorkflow(
            retrieval_service=fake_service,
            query_validator=RetrievalQueryValidator(),
        )
        query = RetrievalQuery(query_id=new_id("q"), query_text="oil change", top_k=5)
        recorder = RetrievalTraceRecorder()

        result = workflow.run(query, trace_recorder=recorder)

        assert result is not None
        trace = recorder.build(query_id=query.query_id, timestamp_iso="2026-01-01T00:00:00")
        assert trace.query_analysis is not None
