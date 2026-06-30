from src.application.langgraph.research import (
    ResearchGoal,
    ResearchGoalType,
    ResearchOutputType,
    ResearchPlan,
    ResearchPlanValidator,
    ResearchTask,
)


def _goal() -> ResearchGoal:
    return ResearchGoal(
        goal_id="goal-1",
        user_input="compare maintenance and specifications",
        goal_type=ResearchGoalType.COMPARISON,
        document_id="doc-42",
        document_title="FWC12 Manual",
        requires_document=True,
        requires_cross_section_reasoning=True,
        requires_multi_strategy_retrieval=True,
        expected_output_type=ResearchOutputType.COMPARISON,
    )


def test_research_plan_validator_rejects_duplicate_task_ids() -> None:
    validator = ResearchPlanValidator()
    plan = ResearchPlan(
        plan_id="plan-1",
        goal=_goal(),
        tasks=[
            ResearchTask(
                task_id="task-1",
                title="Collect maintenance tasks",
                question="What maintenance tasks are described?",
                strategy_hint="MAINTENANCE_LOOKUP",
                answer_intent_hint="comparison",
                document_id="doc-42",
            ),
            ResearchTask(
                task_id="task-1",
                title="Collect technical specifications",
                question="What specifications are described?",
                strategy_hint="TECHNICAL_SPECIFICATION",
                answer_intent_hint="comparison",
                document_id="doc-42",
            ),
        ],
        reason="comparison",
        source="deterministic",
        requires_document=True,
        max_iterations=1,
    )

    validation = validator.validate(plan)

    assert validation.is_valid is False
    assert any(issue.code == "research.plan.task_id.duplicate" for issue in validation.issues)


def test_research_plan_validator_rejects_invalid_dependency() -> None:
    validator = ResearchPlanValidator()
    plan = ResearchPlan(
        plan_id="plan-1",
        goal=_goal(),
        tasks=[
            ResearchTask(
                task_id="task-1",
                title="Collect maintenance tasks",
                question="What maintenance tasks are described?",
                strategy_hint="MAINTENANCE_LOOKUP",
                answer_intent_hint="comparison",
                document_id="doc-42",
                depends_on=["task-2"],
            ),
            ResearchTask(
                task_id="task-2",
                title="Collect technical specifications",
                question="What specifications are described?",
                strategy_hint="TECHNICAL_SPECIFICATION",
                answer_intent_hint="comparison",
                document_id="doc-42",
            ),
        ],
        reason="comparison",
        source="deterministic",
        requires_document=True,
        max_iterations=1,
    )

    validation = validator.validate(plan)

    assert validation.is_valid is False
    assert any(issue.code == "research.plan.depends_on.invalid" for issue in validation.issues)
