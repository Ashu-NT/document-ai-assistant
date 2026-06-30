from src.application.langgraph.research.models import ResearchReport
from src.application.langgraph.research.policies import ResearchSynthesisPolicy
from src.application.langgraph.research.presentation import (
    EnterpriseResearchReportFormatter,
)


def test_enterprise_research_report_formatter_renders_clean_report() -> None:
    formatter = EnterpriseResearchReportFormatter()
    report = ResearchReport(
        title="Comparison Summary",
        executive_summary=(
            "The selected document separates maintenance tasks from technical specifications.\n\n"
            "Maintenance findings focus on inspections, lubrication, and scheduled servicing."
        ),
        sections=[
            {
                "title": "Maintenance Tasks",
                "findings": [
                    {
                        "text": "Operators must isolate electrical power before servicing.",
                        "document_title": "FWC12 Manual",
                        "page_start": 58,
                        "page_end": 58,
                        "section_path": [
                            "7 Components",
                            "7.2 Food Waste Press",
                            "Preventive Maintenance",
                        ],
                    },
                    {
                        "text": "Screen basket cleaning requires the pneumatic cylinder to be depressurized.",
                        "document_title": "FWC12 Manual",
                        "page_start": 59,
                        "page_end": 59,
                        "section_path": [
                            "7 Components",
                            "7.2 Food Waste Press",
                            "Preventive Maintenance",
                        ],
                    },
                ],
            },
            {
                "title": "Technical Specifications",
                "findings": [
                    {
                        "text": "Operating voltage is 400 V / 50 Hz.",
                        "document_title": "FWC12 Manual",
                        "page_start": 50,
                        "page_end": 50,
                        "section_path": [
                            "3 Specifications",
                            "Technical Data",
                        ],
                    }
                ],
            },
        ],
        references=[
            {
                "chunk_id": "chunk-1",
                "document_id": "doc_abc123",
                "document_title": "FWC12 Manual",
                "page_start": 58,
                "page_end": 58,
                "section_path": [
                    "7 Components",
                    "7.2 Food Waste Press",
                    "Preventive Maintenance",
                ],
            },
            {
                "chunk_id": "chunk-2",
                "document_id": "doc_abc123",
                "document_title": "FWC12 Manual",
                "page_start": 59,
                "page_end": 59,
                "section_path": [
                    "7 Components",
                    "7.2 Food Waste Press",
                    "Preventive Maintenance",
                ],
            },
            {
                "chunk_id": "chunk-3",
                "document_id": "doc_abc123",
                "document_title": "FWC12 Manual",
                "page_start": 50,
                "page_end": 50,
                "section_path": [
                    "3 Specifications",
                    "Technical Data",
                ],
            },
        ],
    )

    text = formatter.render(report, policy=ResearchSynthesisPolicy())

    assert "==================================================" in text
    assert "Executive Summary" in text
    assert "(FWC12 Manual, p.58)" in text
    assert "(FWC12 Manual, p.59)" in text
    assert "(FWC12 Manual, p.50)" in text
    assert "[1] FWC12 Manual, pp.50, 58–59" in text
    assert "Sections: Food Waste Press -> Preventive Maintenance; Specifications -> Technical Data" in text
    assert "doc_abc123" not in text
    assert "chunk-1" not in text
