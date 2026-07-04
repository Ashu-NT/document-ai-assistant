from src.application.langgraph.research import (
    DeterministicResearchPlanner,
    ResearchGoalType,
    ResearchPolicy,
)
from src.application.langgraph.strategy_advisor import (
    StrategyAdvisorIntent,
    StrategyAdvisorProposal,
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
        "Collect evidence for maintenance tasks",
        "Collect evidence for specifications",
        "Collect overlap evidence",
        "Collect distinguishing evidence",
    ]
    assert all(task.document_id == "doc-42" for task in plan.tasks)


def test_deterministic_research_planner_extracts_identifier_value_from_full_request() -> None:
    """`_keyword_concepts` matches the category label ("part number"), not the
    value itself — the value only appears elsewhere in the raw request. The
    planner must fall back to searching the full request text, or
    `identifier_value` silently never gets populated for this (the most
    common) identifier-lookup phrasing."""
    planner = DeterministicResearchPlanner()

    plan = planner.plan(
        user_input="What is part number MK311007 used for?",
        document_id="doc-42",
        document_title="FWC12 Manual",
        policy=ResearchPolicy(),
    )

    identifier_task = next(
        task for task in plan.tasks if task.strategy_hint == "IDENTIFIER_LOOKUP"
    )
    assert identifier_task.diagnostics["identifier_value"] == "MK311007"


def test_deterministic_research_planner_extracts_identifier_value_per_comparison_concept() -> None:
    """Comparison concepts (split on 'and'/'versus') already carry the value
    directly in `concept` — must keep using it rather than only the (single,
    ambiguous) match from the full request, which would wrongly assign the
    same value to every concept in the comparison."""
    planner = DeterministicResearchPlanner()

    plan = planner.plan(
        user_input="compare part number MK311007 and part number MK311008",
        document_id="doc-42",
        document_title="FWC12 Manual",
        policy=ResearchPolicy(),
    )

    identifier_tasks = [
        task for task in plan.tasks if task.strategy_hint == "IDENTIFIER_LOOKUP"
    ]
    assert len(identifier_tasks) == 2
    assert {task.diagnostics.get("identifier_value") for task in identifier_tasks} == {
        "MK311007",
        "MK311008",
    }


def test_deterministic_research_planner_omits_identifier_value_when_none_present() -> None:
    planner = DeterministicResearchPlanner()

    plan = planner.plan(
        user_input="What is the part number used for the ball valve assembly?",
        document_id="doc-42",
        document_title="FWC12 Manual",
        policy=ResearchPolicy(),
    )

    identifier_task = next(
        task for task in plan.tasks if task.strategy_hint == "IDENTIFIER_LOOKUP"
    )
    assert "identifier_value" not in identifier_task.diagnostics


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
        "Collect evidence for preventive maintenance",
        "Collect overview evidence",
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
        "Collect evidence for commissioning",
        "Collect safety warnings",
        "Collect prerequisites",
    ]


def test_deterministic_research_planner_uses_advisor_concepts_for_multi_concept_comparison() -> None:
    planner = DeterministicResearchPlanner()

    plan = planner.plan(
        user_input="contrast fault recovery with scheduled servicing",
        document_id="doc-42",
        document_title="FWC12 Manual",
        policy=ResearchPolicy(),
        advisor_proposal=StrategyAdvisorProposal(
            intent=StrategyAdvisorIntent.COMPARISON,
            route="deep_research",
            confidence=0.93,
            concepts=["fault recovery", "scheduled servicing"],
            recommended_strategies=[],
            comparison=True,
            requires_table=False,
            reason="The query compares two maintenance-related concepts.",
        ),
    )

    assert [task.title for task in plan.tasks[:2]] == [
        "Collect evidence for fault recovery",
        "Collect evidence for scheduled servicing",
    ]
    assert plan.goal.diagnostics["concepts"] == [
        "fault recovery",
        "scheduled servicing",
    ]
