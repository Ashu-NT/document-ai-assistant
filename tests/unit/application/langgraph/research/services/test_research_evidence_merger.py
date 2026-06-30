from src.application.langgraph.research import ResearchEvidence, ResearchEvidenceMerger


def test_research_evidence_merger_keeps_same_chunk_for_different_tasks() -> None:
    merger = ResearchEvidenceMerger()

    evidence = [
        ResearchEvidence(
            evidence_id="evidence-1",
            task_id="task-maintenance",
            chunk_id="chunk-1",
            document_id="doc-42",
            document_title="FWC12 Manual",
            section_path=["6 Maintenance"],
            page_start=12,
            page_end=12,
            chunk_type="maintenance_procedure",
            score=0.91,
            content_excerpt="Lubricate bearings every 250 hours.",
            source_tool="retrieve_chunks",
        ),
        ResearchEvidence(
            evidence_id="evidence-2",
            task_id="task-specifications",
            chunk_id="chunk-1",
            document_id="doc-42",
            document_title="FWC12 Manual",
            section_path=["3 Specifications"],
            page_start=12,
            page_end=12,
            chunk_type="technical_specification",
            score=0.88,
            content_excerpt="Operating pressure is 2.0 bar.",
            source_tool="retrieve_chunks",
        ),
    ]

    merged = merger.merge(evidence, max_total_evidence=10)

    assert len(merged) == 2
    assert {item.task_id for item in merged} == {
        "task-maintenance",
        "task-specifications",
    }


def test_research_evidence_merger_dedupes_same_chunk_within_same_task() -> None:
    merger = ResearchEvidenceMerger()

    merged = merger.merge(
        [
            ResearchEvidence(
                evidence_id="evidence-1",
                task_id="task-1",
                chunk_id="chunk-1",
                document_id="doc-42",
                document_title="FWC12 Manual",
                section_path=["6 Maintenance"],
                page_start=12,
                page_end=12,
                chunk_type="maintenance_procedure",
                score=0.42,
                content_excerpt="Lower score evidence.",
                source_tool="retrieve_chunks",
            ),
            ResearchEvidence(
                evidence_id="evidence-2",
                task_id="task-1",
                chunk_id="chunk-1",
                document_id="doc-42",
                document_title="FWC12 Manual",
                section_path=["6 Maintenance"],
                page_start=12,
                page_end=12,
                chunk_type="maintenance_procedure",
                score=0.91,
                content_excerpt="Higher score evidence.",
                source_tool="retrieve_chunks",
            ),
        ],
        max_total_evidence=10,
    )

    assert len(merged) == 1
    assert merged[0].evidence_id == "evidence-2"
