from types import SimpleNamespace

from src.application.langgraph.research import EvidenceCoverageEvaluator, ResearchTask


def test_evidence_coverage_evaluator_reports_concept_coverage() -> None:
    evaluator = EvidenceCoverageEvaluator()
    plan = SimpleNamespace(
        tasks=[
            ResearchTask(
                task_id="task-1",
                title="Collect evidence for maintenance",
                question="What evidence describes maintenance?",
                strategy_hint="MAINTENANCE_LOOKUP",
                answer_intent_hint="comparison",
                document_id="doc-42",
                diagnostics={"concept": "maintenance"},
            ),
            ResearchTask(
                task_id="task-2",
                title="Collect evidence for troubleshooting",
                question="What evidence describes troubleshooting?",
                strategy_hint="TROUBLESHOOTING_LOOKUP",
                answer_intent_hint="comparison",
                document_id="doc-42",
                diagnostics={"concept": "troubleshooting"},
            ),
        ]
    )
    result = SimpleNamespace(
        plan=plan,
        goal=SimpleNamespace(diagnostics={"concepts": ["maintenance", "troubleshooting"]}),
        task_results=[
            SimpleNamespace(task_id="task-1", success=True, evidence=[object()]),
            SimpleNamespace(task_id="task-2", success=True, evidence=[]),
        ],
        evidence=[SimpleNamespace(page_start=1, page_end=1, section_path=["Maintenance"])],
    )

    coverage = evaluator.evaluate(result)

    assert coverage["concept_coverage_ratio"] == 0.5
    assert coverage["covered_concepts"] == ["maintenance"]
    assert coverage["uncovered_concepts"] == ["troubleshooting"]
