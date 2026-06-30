from src.application.langgraph.research.models import (
    ResearchEvidence,
    ResearchGoal,
    ResearchGoalType,
    ResearchOutputType,
    ResearchPlan,
    ResearchResult,
    ResearchTask,
    ResearchTaskResult,
)
from src.application.langgraph.research.synthesizers.comparison_synthesizer import (
    ComparisonSynthesizer,
)


def test_comparison_synthesizer_adds_comparison_section() -> None:
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
    maintenance_task = ResearchTask(
        task_id="task-1",
        title="Collect maintenance tasks",
        question="What maintenance tasks are described?",
        strategy_hint="MAINTENANCE_LOOKUP",
        answer_intent_hint="comparison",
        document_id="doc-42",
    )
    specification_task = ResearchTask(
        task_id="task-2",
        title="Collect technical specifications",
        question="What technical specifications are described?",
        strategy_hint="TECHNICAL_SPECIFICATION",
        answer_intent_hint="comparison",
        document_id="doc-42",
    )
    maintenance_evidence = ResearchEvidence(
        evidence_id="evidence-1",
        task_id="task-1",
        chunk_id="chunk-1",
        document_id="doc-42",
        document_title="FWC12 Manual",
        section_path=["Preventive Maintenance"],
        page_start=58,
        page_end=58,
        chunk_type="maintenance_procedure",
        score=0.9,
        content_excerpt="Isolate power before servicing the press.",
        source_tool="retrieve_chunks",
    )
    specification_evidence = ResearchEvidence(
        evidence_id="evidence-2",
        task_id="task-2",
        chunk_id="chunk-2",
        document_id="doc-42",
        document_title="FWC12 Manual",
        section_path=["Technical Data"],
        page_start=50,
        page_end=50,
        chunk_type="technical_specification",
        score=0.88,
        content_excerpt="| Press Type | TSP20 | | Voltage | 400 V / 50 Hz |",
        source_tool="retrieve_chunks",
    )
    result = ResearchResult(
        success=True,
        goal=goal,
        plan=ResearchPlan(
            plan_id="plan-1",
            goal=goal,
            tasks=[maintenance_task, specification_task],
            reason="comparison",
            source="deterministic",
            requires_document=True,
            max_iterations=1,
        ),
        task_results=[
            ResearchTaskResult(
                task_id="task-1",
                success=True,
                evidence=[maintenance_evidence],
            ),
            ResearchTaskResult(
                task_id="task-2",
                success=True,
                evidence=[specification_evidence],
            ),
        ],
        evidence=[maintenance_evidence, specification_evidence],
    )

    synthesis = ComparisonSynthesizer().synthesize(result)

    assert synthesis.sections[-1]["title"] == "Comparison"
    comparison_texts = [finding["text"] for finding in synthesis.sections[-1]["findings"]]
    assert any(
        "Maintenance findings describe required actions" in text
        for text in comparison_texts
    )
    assert any(
        "Technical specification findings describe equipment identity" in text
        for text in comparison_texts
    )
