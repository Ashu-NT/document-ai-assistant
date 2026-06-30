from src.application.langgraph.research import (
    DeterministicResearchPlanner,
    ResearchGoalType,
    ResearchPolicy,
)


def test_deterministic_research_planner_builds_comparison_tasks() -> None:
    planner = DeterministicResearchPlanner()

    plan = planner.plan(
        user_input="compare maintenance tasks and specifications",
        document_id="doc-42",
        document_title="FWC12 Manual",
        policy=ResearchPolicy(),
    )

    assert plan.goal.goal_type == ResearchGoalType.COMPARISON
    assert [task.title for task in plan.tasks] == [
        "Collect maintenance tasks",
        "Collect technical specifications",
    ]
    assert all(task.document_id == "doc-42" for task in plan.tasks)


def test_deterministic_research_planner_builds_maintenance_report_tasks() -> None:
    planner = DeterministicResearchPlanner()

    plan = planner.plan(
        user_input="generate a preventive maintenance report",
        document_id="doc-42",
        document_title="FWC12 Manual",
        policy=ResearchPolicy(),
    )

    assert plan.goal.goal_type == ResearchGoalType.REPORT
    assert [task.title for task in plan.tasks] == [
        "Collect maintenance tasks",
        "Collect maintenance intervals",
        "Collect safety notes",
    ]


def test_deterministic_research_planner_builds_checklist_tasks() -> None:
    planner = DeterministicResearchPlanner()

    plan = planner.plan(
        user_input="create a commissioning checklist",
        document_id="doc-42",
        document_title="FWC12 Manual",
        policy=ResearchPolicy(),
    )

    assert plan.goal.goal_type == ResearchGoalType.CHECKLIST
    assert [task.title for task in plan.tasks] == [
        "Collect commissioning procedures",
        "Collect safety warnings",
        "Collect prerequisites",
    ]
