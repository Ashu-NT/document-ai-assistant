from src.application.langgraph.research.evaluators import ResearchGapDetector
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


def _build_gap_analysis_result(*, content_excerpt: str) -> ResearchResult:
    goal = ResearchGoal(
        goal_id="goal-1",
        user_input="identify missing evidence for oil change interval",
        goal_type=ResearchGoalType.GAP_ANALYSIS,
        document_id="doc-42",
        document_title="FWC12 Manual",
        requires_document=True,
        requires_cross_section_reasoning=True,
        requires_multi_strategy_retrieval=True,
        expected_output_type=ResearchOutputType.EVIDENCE_REVIEW,
    )
    task = ResearchTask(
        task_id="task-1",
        title="Collect primary evidence",
        question=goal.user_input,
        strategy_hint="GENERAL_HYBRID",
        answer_intent_hint="evidence_review",
        document_id="doc-42",
        expected_evidence_type="claim_evidence",
    )
    evidence = ResearchEvidence(
        evidence_id="evidence-1",
        task_id="task-1",
        chunk_id="chunk-1",
        document_id="doc-42",
        document_title="FWC12 Manual",
        section_path=["Maintenance", "Lubrication Schedule"],
        page_start=79,
        page_end=79,
        chunk_type="maintenance_interval",
        score=0.81,
        content_excerpt=content_excerpt,
        source_tool="retrieve_chunks",
    )
    return ResearchResult(
        success=True,
        goal=goal,
        plan=ResearchPlan(
            plan_id="plan-1",
            goal=goal,
            tasks=[task],
            reason="gap analysis",
            source="deterministic",
            requires_document=True,
            max_iterations=1,
        ),
        task_results=[ResearchTaskResult(task_id="task-1", success=True, evidence=[evidence])],
        evidence=[evidence],
    )


def test_research_gap_detector_flags_uncovered_focus_terms_for_gap_analysis() -> None:
    detector = ResearchGapDetector()
    result = _build_gap_analysis_result(
        content_excerpt="Lubricate the shaft seals every 350 operating hours."
    )

    gaps = detector.detect(result, coverage={"section_count": 2})

    assert gaps
    assert "change" in gaps[0].diagnostics["uncovered_focus_terms"]


def test_research_gap_detector_flags_scattered_terms_without_direct_joint_evidence() -> None:
    detector = ResearchGapDetector()
    result = _build_gap_analysis_result(
        content_excerpt="Oil quantities are listed for service planning."
    )
    result.evidence.append(
        ResearchEvidence(
            evidence_id="evidence-2",
            task_id="task-1",
            chunk_id="chunk-2",
            document_id="doc-42",
            document_title="FWC12 Manual",
            section_path=["Maintenance", "General Notes"],
            page_start=80,
            page_end=80,
            chunk_type="general",
            score=0.55,
            content_excerpt="Change the grease carefully during overhaul work.",
            source_tool="retrieve_chunks",
        )
    )
    result.evidence.append(
        ResearchEvidence(
            evidence_id="evidence-3",
            task_id="task-1",
            chunk_id="chunk-3",
            document_id="doc-42",
            document_title="FWC12 Manual",
            section_path=["Maintenance", "Intervals"],
            page_start=81,
            page_end=81,
            chunk_type="maintenance_interval",
            score=0.65,
            content_excerpt="Interval schedule for inspection tasks.",
            source_tool="retrieve_chunks",
        )
    )
    result.task_results[0].evidence = list(result.evidence)

    gaps = detector.detect(result, coverage={"section_count": 2})

    assert gaps
    assert "max_focus_terms_in_single_evidence" in gaps[0].diagnostics


def test_research_gap_detector_does_not_flag_gap_when_focus_terms_are_covered() -> None:
    detector = ResearchGapDetector()
    result = _build_gap_analysis_result(
        content_excerpt="Oil change interval: change the oil every 350 operating hours."
    )

    gaps = detector.detect(result, coverage={"section_count": 2})

    assert gaps == []


def test_research_gap_detector_flags_gap_probe_sections_without_complete_direct_evidence() -> None:
    detector = ResearchGapDetector()
    result = _build_gap_analysis_result(
        content_excerpt="Oil change interval: change the oil every 350 operating hours."
    )
    gap_probe_task = ResearchTask(
        task_id="task-2",
        title="Collect potentially missing or contradicting sections",
        question="What sections are related to this request but do not provide direct evidence?",
        strategy_hint="SECTION_LOOKUP",
        answer_intent_hint="evidence_review",
        document_id="doc-42",
        required=False,
        expected_evidence_type="gap_probe",
    )
    gap_probe_evidence = ResearchEvidence(
        evidence_id="evidence-2",
        task_id="task-2",
        chunk_id="chunk-2",
        document_id="doc-42",
        document_title="FWC12 Manual",
        section_path=["Storage", "General"],
        page_start=75,
        page_end=75,
        chunk_type="general",
        score=0.41,
        content_excerpt="General storage guidance for rubber parts.",
        source_tool="retrieve_chunks",
    )
    result.plan.tasks.append(gap_probe_task)
    result.task_results.append(
        ResearchTaskResult(task_id="task-2", success=True, evidence=[gap_probe_evidence])
    )
    result.evidence.append(gap_probe_evidence)

    gaps = detector.detect(result, coverage={"section_count": 3})

    assert gaps
    assert "gap_probe_evidence_count" in gaps[0].diagnostics
