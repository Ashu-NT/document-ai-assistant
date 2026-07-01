from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_corpus_seeder import (
    RetrievalBenchmarkCorpusSeeder,
    _CorpusSeedTarget,
)
from src.application.workflows.ingestion.ingestion_result import IngestionResult
from src.application.workflows.ingestion.ingestion_status import IngestionStatus


class FakeIngestionWorkflow:
    def __init__(self, document_id="doc_123"):
        self.calls = []
        self._document_id = document_id

    def run(self, request, *, progress_callback=None):
        self.calls.append(request)
        return IngestionResult(
            status=IngestionStatus.COMPLETE,
            ingestion_run_id="run_001",
            document_id=self._document_id,
            file_name="test.pdf",
            current_stage=None,
        )


class FakeDocumentLookupService:
    def __init__(self, graph):
        self._graph = graph

    def get_document_graph(self, document_id, activity_context=None):
        return self._graph


class FakeClassificationService:
    def __init__(self, classification=None):
        self._classification = classification

    def get_document_classification(self, document_id):
        return self._classification


def _make_seeder(ingestion_workflow, document_graph, classification=None):
    return RetrievalBenchmarkCorpusSeeder(
        parsing_workflow=None,
        document_registration_service=None,
        duplicate_detection_service=None,
        document_lookup_service=FakeDocumentLookupService(document_graph),
        classification_service=FakeClassificationService(classification),
        document_classification_workflow=None,
        post_classification_chunk_finalization_workflow=None,
        ingestion_workflow=ingestion_workflow,
    )


def test_seeder_uses_ingestion_workflow_for_new_document(
    sample_document_graph,
):
    doc_id = sample_document_graph.document.document_id
    ingestion_workflow = FakeIngestionWorkflow(document_id=doc_id)
    seeder = _make_seeder(ingestion_workflow, sample_document_graph)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\ntest")
        tmp_path = Path(f.name)

    try:
        seed_target = _CorpusSeedTarget(
            document_alias="test_doc",
            file_name=tmp_path.name,
            file_path=tmp_path,
        )
        final_graph, classification, status = seeder._seed_new_document(
            seed_target=seed_target,
            file_hash="abc123",
        )
        assert len(ingestion_workflow.calls) == 1
        assert ingestion_workflow.calls[0].force is True
        assert ingestion_workflow.calls[0].requested_by == "benchmark_seeder"
        assert status == "seeded_new"
        assert final_graph.document.document_id == doc_id
    finally:
        tmp_path.unlink(missing_ok=True)
