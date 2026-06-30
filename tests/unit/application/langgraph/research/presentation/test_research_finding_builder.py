from src.application.langgraph.research import ResearchEvidence, ResearchFindingBuilder


def test_research_finding_builder_summarizes_markdown_table_rows() -> None:
    builder = ResearchFindingBuilder()

    findings = builder.build_findings(
        [
            ResearchEvidence(
                evidence_id="evidence-1",
                task_id="task-1",
                chunk_id="chunk-1",
                document_id="doc-42",
                document_title="FWC12 Manual",
                section_path=["Technical Data"],
                page_start=50,
                page_end=50,
                chunk_type="technical_specification",
                score=0.92,
                content_excerpt=(
                    "| Press Type | Serial Number | Voltage |\n"
                    "| --- | --- | --- |\n"
                    "| FWC12 | SN-001 | 400 V / 50 Hz |"
                ),
                source_tool="retrieve_chunks",
            )
        ]
    )

    assert findings
    assert findings[0]["text"] == "Technical specifications include:"
    assert findings[0]["details"][:3] == [
        "Press Type: FWC12",
        "Serial Number: SN-001",
        "Voltage: 400 V / 50 Hz",
    ]


def test_research_finding_builder_ignores_scaffolding_prefixes_and_warning_headings() -> None:
    builder = ResearchFindingBuilder()

    findings = builder.build_findings(
        [
            ResearchEvidence(
                evidence_id="evidence-1",
                task_id="task-1",
                chunk_id="chunk-1",
                document_id="doc-42",
                document_title="FWC12 Manual",
                section_path=["Preventive Maintenance"],
                page_start=58,
                page_end=59,
                chunk_type="maintenance_procedure",
                score=0.91,
                content_excerpt=(
                    "Section overview:\n"
                    "WARNING\n"
                    "Operators must isolate electrical power before servicing.\n"
                ),
                source_tool="retrieve_chunks",
            )
        ]
    )

    assert findings == [
        {
            "text": "Operators must isolate electrical power before servicing.",
            "document_title": "FWC12 Manual",
            "page_start": 58,
            "page_end": 59,
            "section_path": ["Preventive Maintenance"],
            "chunk_type": "maintenance_procedure",
        }
    ]


def test_research_finding_builder_skips_truncated_excerpt() -> None:
    builder = ResearchFindingBuilder()

    findings = builder.build_findings(
        [
            ResearchEvidence(
                evidence_id="evidence-1",
                task_id="task-1",
                chunk_id="chunk-1",
                document_id="doc-42",
                document_title="FWC12 Manual",
                section_path=["Preventive Maintenance"],
                page_start=58,
                page_end=58,
                chunk_type="maintenance_procedure",
                score=0.91,
                content_excerpt="Disconnect the air line before servicing...",
                source_tool="retrieve_chunks",
            )
        ]
    )

    assert findings == []
