import json

from src.application.langgraph.research.models import ResearchEvidence
from src.application.langgraph.research.presentation.evidence_finding_extractor import (
    EvidenceFindingExtractor,
)


def _make_evidence(*, content_excerpt: str, diagnostics: dict | None = None) -> ResearchEvidence:
    return ResearchEvidence(
        evidence_id="ev_1",
        task_id="task_1",
        chunk_id="chunk_1",
        document_id="doc_1",
        document_title="Manual",
        section_path=["Specifications"],
        page_start=1,
        page_end=1,
        chunk_type="technical_specification",
        score=0.9,
        content_excerpt=content_excerpt,
        source_tool="retrieve_chunks",
        diagnostics=diagnostics or {},
    )


def test_extract_uses_structured_rows_from_diagnostics_when_present() -> None:
    extractor = EvidenceFindingExtractor()
    evidence = _make_evidence(
        content_excerpt="| Parameter | Value |\n|---|---|\n| Voltage (text) | 12 V |",
        diagnostics={
            "table_rows_json": json.dumps(
                [["Parameter", "Value"], ["Voltage", "24 V"], ["Pressure", "10 bar"]]
            )
        },
    )

    findings = extractor.extract(evidence)

    assert len(findings) == 1
    assert "Voltage: 24 V" in findings[0]["details"]
    assert "Voltage: 12 V" not in findings[0]["details"]


def test_extract_falls_back_to_text_parsing_without_diagnostics() -> None:
    extractor = EvidenceFindingExtractor()
    evidence = _make_evidence(
        content_excerpt="| Parameter | Value |\n|---|---|\n| Voltage | 24 V |\n| Pressure | 10 bar |",
    )

    findings = extractor.extract(evidence)

    assert len(findings) == 1
    assert "Voltage: 24 V" in findings[0]["details"]


def test_extract_falls_back_to_text_parsing_when_table_rows_json_malformed() -> None:
    extractor = EvidenceFindingExtractor()
    evidence = _make_evidence(
        content_excerpt="| Parameter | Value |\n|---|---|\n| Voltage | 24 V |\n| Pressure | 10 bar |",
        diagnostics={"table_rows_json": "not valid json"},
    )

    findings = extractor.extract(evidence)

    assert len(findings) == 1
    assert "Voltage: 24 V" in findings[0]["details"]
