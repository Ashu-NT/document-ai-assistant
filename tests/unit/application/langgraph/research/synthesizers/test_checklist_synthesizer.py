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
from src.application.langgraph.research.synthesizers.checklist_synthesizer import (
    ChecklistSynthesizer,
)


def test_checklist_synthesizer_emits_sections_and_checklist_items() -> None:
    goal = ResearchGoal(
        goal_id="goal-1",
        user_input="create a commissioning checklist",
        goal_type=ResearchGoalType.CHECKLIST,
        document_id="doc-42",
        document_title="FWC12 Manual",
        requires_document=True,
        requires_cross_section_reasoning=True,
        requires_multi_strategy_retrieval=False,
        expected_output_type=ResearchOutputType.CHECKLIST,
    )
    task = ResearchTask(
        task_id="task-1",
        title="Collect commissioning procedures",
        question="What startup or commissioning procedures are described?",
        strategy_hint="PROCEDURE_LOOKUP",
        answer_intent_hint="checklist",
        document_id="doc-42",
    )
    evidence = ResearchEvidence(
        evidence_id="evidence-1",
        task_id="task-1",
        chunk_id="chunk-1",
        document_id="doc-42",
        document_title="FWC12 Manual",
        section_path=["Commissioning"],
        page_start=40,
        page_end=40,
        chunk_type="installation_instruction",
        score=0.92,
        content_excerpt="Open valves and vents before starting the pump.",
        source_tool="retrieve_chunks",
    )
    result = ResearchResult(
        success=True,
        goal=goal,
        plan=ResearchPlan(
            plan_id="plan-1",
            goal=goal,
            tasks=[task],
            reason="checklist",
            source="deterministic",
            requires_document=True,
            max_iterations=1,
        ),
        task_results=[ResearchTaskResult(task_id="task-1", success=True, evidence=[evidence])],
        evidence=[evidence],
    )

    synthesis = ChecklistSynthesizer().synthesize(result)

    assert synthesis.sections
    assert synthesis.sections[0]["title"] == "Collect commissioning procedures"
    assert synthesis.checklist_items
    assert synthesis.references[0]["chunk_id"] == "chunk-1"
