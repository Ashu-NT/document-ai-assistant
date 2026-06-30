from types import SimpleNamespace

from src.application.langgraph.nodes.research import ResearchSummaryNode
from src.application.langgraph.research import (
    ResearchEvidence,
    ResearchGoal,
    ResearchGoalType,
    ResearchOutputType,
    ResearchPlan,
    ResearchReport,
    ResearchResult,
    ResearchSynthesisPolicy,
    ResearchTask,
    ResearchTaskResult,
)
from src.application.langgraph.research.services import ResearchStateMapper


def test_research_summary_node_formats_plan_trace_and_citations() -> None:
    goal = ResearchGoal(
        goal_id="goal-1",
        user_input="compare maintenance tasks and specifications",
        goal_type=ResearchGoalType.COMPARISON,
        document_id="doc-42",
        document_title="FWC12 Manual",
        requires_document=True,
        requires_cross_section_reasoning=True,
        requires_multi_strategy_retrieval=True,
        expected_output_type=ResearchOutputType.COMPARISON,
    )
    task = ResearchTask(
        task_id="task-1",
        title="Collect maintenance tasks",
        question="What maintenance tasks are described?",
        strategy_hint="MAINTENANCE_LOOKUP",
        answer_intent_hint="comparison",
        document_id="doc-42",
    )
    plan = ResearchPlan(
        plan_id="plan-1",
        goal=goal,
        tasks=[task],
        reason="comparison",
        source="deterministic",
        requires_document=True,
        max_iterations=1,
    )
    evidence = ResearchEvidence(
        evidence_id="evidence-1",
        task_id="task-1",
        chunk_id="chunk-1",
        document_id="doc-42",
        document_title="FWC12 Manual",
        section_path=["6 Maintenance", "Lubrication"],
        page_start=12,
        page_end=12,
        chunk_type="maintenance_procedure",
        score=0.91,
        content_excerpt="Lubricate the bearings every 250 hours.",
        source_tool="retrieve_chunks",
    )
    report = ResearchReport(
        title="Comparison Summary",
        executive_summary="Maintenance tasks and specifications were compared.",
        sections=[{"title": "Maintenance findings", "body": "Lubrication tasks were found."}],
        references=[
            {
                "document_id": "doc-42",
                "section_path": ["6 Maintenance", "Lubrication"],
                "page_start": 12,
                "page_end": 12,
            }
        ],
    )
    result = ResearchResult(
        success=True,
        goal=goal,
        plan=plan,
        task_results=[ResearchTaskResult(task_id="task-1", success=True, evidence=[evidence])],
        evidence=[evidence],
        report=report,
    )
    state = {
        **ResearchStateMapper.result_to_state(result),
        "research_trace": {
            "plan_source": "deterministic",
            "evidence_counts_per_task": {"task-1": 1},
            "gaps": [],
        },
        "show_research_plan": True,
        "show_research_trace": True,
        "tool_results": {},
        "trace": [],
        "route": "deep_research",
    }
    node = ResearchSummaryNode(
        SimpleNamespace(
            report_builder=SimpleNamespace(
                to_markdown=lambda report, policy: "# Comparison Summary\n\n## Executive Summary\nCompared."
            ),
            synthesis_policy=ResearchSynthesisPolicy(),
        )
    )

    patch = node(state)

    assert "Research Plan" in patch["response_text"]
    assert "Research Trace" in patch["response_text"]
    answer_payload = patch["tool_results"]["answer_question"]["data"]
    assert answer_payload["route"] == "deep_research"
    assert answer_payload["answer_intent"] == "research_comparison"
    assert answer_payload["citations"][0]["chunk_id"] == "chunk-1"
    assert answer_payload["retrieval_result"]["context_chunks"][0]["chunk_id"] == "chunk-1"
