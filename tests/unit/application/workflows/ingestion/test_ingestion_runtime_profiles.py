import pytest

from src.application.workflows.ingestion import IngestionRequest, IngestionStatus
from src.application.workflows.ingestion.models.ingestion_exceptions import (
    IngestionDependencyError,
)
from src.application.workflows.ingestion.runtime import (
    IngestionRuntimeProfile,
    IngestionRuntimeProfileResolver,
)
from tests.unit.application.workflows.ingestion._test_ingestion_workflow_support import (
    FakeSemanticLinkingWorkflow,
    _build_workflow,
)


def test_runtime_profile_auto_resolves_to_structural_only_without_extraction() -> None:
    capabilities = IngestionRuntimeProfileResolver().resolve(
        requested_profile=IngestionRuntimeProfile.AUTO,
        extraction_enabled=False,
        question_generation_enabled=False,
        deterministic_identifier_scan_enabled=True,
        semantic_linking_enabled=True,
    )

    assert capabilities.resolved_profile is IngestionRuntimeProfile.STRUCTURAL_ONLY
    assert capabilities.extraction_enabled is False
    assert capabilities.semantic_linking_enabled is False


def test_runtime_profile_semantic_enriched_requires_extraction() -> None:
    with pytest.raises(IngestionDependencyError):
        IngestionRuntimeProfileResolver().resolve(
            requested_profile=IngestionRuntimeProfile.SEMANTIC_ENRICHED,
            extraction_enabled=False,
            question_generation_enabled=False,
            deterministic_identifier_scan_enabled=False,
            semantic_linking_enabled=False,
        )


def test_ingestion_workflow_does_not_run_semantic_linking_in_structural_mode(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    semantic_linking_workflow = FakeSemanticLinkingWorkflow(relationships=["r1"])
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        semantic_linking_workflow=semantic_linking_workflow,
        extraction_enabled=False,
    )

    result = workflow.run(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert result.status == IngestionStatus.COMPLETE
    assert semantic_linking_workflow.calls == []
    assert result.diagnostics["ingestion_runtime_profile"] == "structural_only"
    assert result.diagnostics["semantic_linking_enabled"] is False
