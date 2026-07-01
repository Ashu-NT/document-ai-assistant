from src.application.langgraph.research import ResearchPlan, ResearchService, ResearchTask


class _InvalidComparisonPlanner:
    def plan(self, *, goal, policy):
        return (
            ResearchPlan(
                plan_id="plan-llm",
                goal=goal,
                tasks=[
                    ResearchTask(
                        task_id="task-1",
                        title="Collect maintenance tasks",
                        question="What maintenance tasks are described?",
                        strategy_hint="MAINTENANCE_LOOKUP",
                        answer_intent_hint="comparison",
                        document_id=goal.document_id,
                        expected_evidence_type="maintenance",
                    )
                ],
                reason="comparison",
                source="llm",
                requires_document=True,
                max_iterations=1,
            ),
            '{"tasks":[{"task_id":"task-1"}]}',
        )


def test_research_service_falls_back_to_deterministic_plan_for_invalid_llm_comparison() -> None:
    service = ResearchService(llm_planner=_InvalidComparisonPlanner())

    plan, diagnostics = service.plan_research(
        user_input="compare maintenance tasks and specifications",
        document_id="doc-42",
        document_title="FWC12 Manual",
        use_llm_planner=True,
    )

    assert diagnostics["planning_source"] == "deterministic"
    assert diagnostics["raw_llm_plan"] == '{"tasks":[{"task_id":"task-1"}]}'
    assert [task.title for task in plan.tasks] == [
        "Collect evidence for maintenance tasks",
        "Collect evidence for specifications",
        "Collect overlap evidence",
        "Collect distinguishing evidence",
    ]
