from __future__ import annotations

from dataclasses import replace
from typing import Any

from src.application.langgraph.research.executors.research_executor import (
    ResearchExecutor,
)
from src.application.langgraph.research.models import (
    ResearchPlan,
    ResearchResult,
    ResearchTask,
)
from src.application.langgraph.research.executors.research_iteration_controller import (
    ResearchIterationController,
)
from src.application.langgraph.research.planners.deterministic_research_planner import (
    DeterministicResearchPlanner,
)
from src.application.langgraph.research.planners.llm_research_planner import (
    LLMResearchPlanner,
)
from src.application.langgraph.research.planners.research_plan_repair import (
    ResearchPlanRepair,
)
from src.application.langgraph.research.policies import (
    ResearchIterationPolicy,
    ResearchPolicy,
    ResearchSynthesisPolicy,
)
from src.application.langgraph.research.services.research_context_builder import (
    ResearchContextBuilder,
)
from src.application.langgraph.research.services.research_evidence_merger import (
    ResearchEvidenceMerger,
)
from src.application.langgraph.research.synthesizers.research_report_builder import (
    ResearchReportBuilder,
)
from src.application.langgraph.research.evaluators.evidence_coverage_evaluator import (
    EvidenceCoverageEvaluator,
)
from src.application.langgraph.research.evaluators.research_gap_detector import (
    ResearchGapDetector,
)
from src.application.langgraph.research.evaluators.research_quality_evaluator import (
    ResearchQualityEvaluator,
)
from src.application.langgraph.research.validation.research_plan_validator import (
    ResearchPlanValidator,
)
from src.application.langgraph.research.validation.research_report_validator import (
    ResearchReportValidator,
)
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorProposal,
)
from src.shared.exceptions import SchemaValidationError


class ResearchService:
    def __init__(
        self,
        *,
        deterministic_planner: DeterministicResearchPlanner | None = None,
        llm_planner: LLMResearchPlanner | None = None,
        plan_validator: ResearchPlanValidator | None = None,
        plan_repair: ResearchPlanRepair | None = None,
        executor: ResearchExecutor | None = None,
        evidence_merger: ResearchEvidenceMerger | None = None,
        gap_detector: ResearchGapDetector | None = None,
        coverage_evaluator: EvidenceCoverageEvaluator | None = None,
        quality_evaluator: ResearchQualityEvaluator | None = None,
        context_builder: ResearchContextBuilder | None = None,
        report_builder: ResearchReportBuilder | None = None,
        report_validator: ResearchReportValidator | None = None,
        iteration_controller: ResearchIterationController | None = None,
        policy: ResearchPolicy | None = None,
        iteration_policy: ResearchIterationPolicy | None = None,
        synthesis_policy: ResearchSynthesisPolicy | None = None,
    ) -> None:
        self.deterministic_planner = deterministic_planner or DeterministicResearchPlanner()
        self.llm_planner = llm_planner
        self.plan_validator = plan_validator or ResearchPlanValidator()
        self.plan_repair = plan_repair or ResearchPlanRepair()
        self.executor = executor or ResearchExecutor()
        self.evidence_merger = evidence_merger or ResearchEvidenceMerger()
        self.gap_detector = gap_detector or ResearchGapDetector()
        self.coverage_evaluator = coverage_evaluator or EvidenceCoverageEvaluator()
        self.quality_evaluator = quality_evaluator or ResearchQualityEvaluator()
        self.context_builder = context_builder or ResearchContextBuilder()
        self.report_builder = report_builder or ResearchReportBuilder()
        self.report_validator = report_validator or ResearchReportValidator()
        self.iteration_controller = iteration_controller or ResearchIterationController()
        self.policy = policy or ResearchPolicy()
        self.iteration_policy = iteration_policy or ResearchIterationPolicy()
        self.synthesis_policy = synthesis_policy or ResearchSynthesisPolicy()

    def plan_research(
        self,
        *,
        user_input: str,
        document_id: str | None,
        document_title: str | None,
        advisor_proposal: StrategyAdvisorProposal | None = None,
        use_llm_planner: bool = False,
    ) -> tuple[ResearchPlan, dict[str, Any]]:
        deterministic_plan = self.deterministic_planner.plan(
            user_input=user_input,
            document_id=document_id,
            document_title=document_title,
            policy=self.policy,
            advisor_proposal=advisor_proposal,
        )
        diagnostics: dict[str, Any] = {
            "planning_source": "deterministic",
            "planning_warnings": [],
            "planning_errors": [],
            "raw_llm_plan": None,
            "advisor_concepts": (
                list(advisor_proposal.concepts)
                if advisor_proposal is not None
                else list(
                    (deterministic_plan.goal.diagnostics or {}).get("concepts", [])
                )
            ),
        }
        accepted_plan = deterministic_plan

        if use_llm_planner and self.llm_planner is not None:
            try:
                llm_plan, raw_payload = self.llm_planner.plan(
                    goal=deterministic_plan.goal,
                    policy=self.policy,
                )
                if self.plan_validator.validate(llm_plan).is_valid:
                    accepted_plan = llm_plan
                    diagnostics["planning_source"] = "llm"
                diagnostics["raw_llm_plan"] = raw_payload
            except Exception as exc:
                diagnostics["planning_warnings"] = [
                    f"LLM research planning fallback failed: {exc}"
                ]

        validation = self.plan_validator.validate(accepted_plan)
        if validation.is_valid:
            return accepted_plan, diagnostics

        repaired_plan, repair_diagnostics = self.plan_repair.repair(
            accepted_plan,
            document_id=document_id,
            policy=self.policy,
        )
        diagnostics["planning_warnings"] = [
            *diagnostics.get("planning_warnings", []),
            *repair_diagnostics.get("changes", []),
        ]
        diagnostics["planning_errors"] = [
            issue.message for issue in validation.issues
        ]
        repaired_validation = self.plan_validator.validate(repaired_plan)
        if repaired_validation.is_valid:
            diagnostics["planning_source"] = repaired_plan.source
            return repaired_plan, diagnostics

        raise SchemaValidationError(
            "Research plan validation failed.",
            details={
                "issues": [issue.message for issue in repaired_validation.issues],
                **diagnostics,
            },
        )

    def execute_research(
        self,
        *,
        plan: ResearchPlan,
        tool_registry,
        current_result: ResearchResult | None = None,
        use_llm_strategy: bool = False,
    ) -> ResearchResult:
        result = self.executor.execute(
            plan,
            tool_registry=tool_registry,
            current_result=current_result,
            use_llm_strategy=use_llm_strategy,
        )
        merged = self.evidence_merger.merge(
            result.evidence,
            max_total_evidence=self.policy.max_total_evidence,
        )
        result.evidence = merged
        required_task_ids = {
            task.task_id
            for task in plan.tasks
            if task.required
        }
        failed_required_tasks = {
            task_result.task_id
            for task_result in result.task_results
            if task_result.task_id in required_task_ids and not task_result.success
        }
        result.success = len(failed_required_tasks) == 0
        return result

    def evaluate_research(
        self,
        result: ResearchResult,
    ) -> tuple[ResearchResult, list[ResearchTask]]:
        coverage = self.coverage_evaluator.evaluate(result)
        gaps = self.gap_detector.detect(result, coverage=coverage)
        followup_tasks = self.iteration_controller.build_followup_tasks(
            result,
            gaps,
            iteration_policy=self.iteration_policy,
            research_policy=self.policy,
        )
        result.gaps = gaps
        result.diagnostics["coverage"] = coverage
        result.diagnostics["quality"] = self.quality_evaluator.evaluate(result)
        return result, followup_tasks

    def synthesize_research(self, result: ResearchResult) -> ResearchResult:
        context = self.context_builder.build(
            evidence=result.evidence,
            gaps=result.gaps,
        )
        synthesis = self.report_builder.build_synthesis(result)
        report = self.report_builder.build_report(
            result=result,
            synthesis=synthesis,
            context=context,
            policy=self.synthesis_policy,
        )
        validation = self.report_validator.validate(report)
        validation.raise_if_invalid()
        result.synthesis = synthesis
        result.report = report
        return result

    def append_followup_tasks(
        self,
        plan: ResearchPlan,
        followup_tasks: list[ResearchTask],
    ) -> ResearchPlan:
        if not followup_tasks:
            return plan
        return replace(plan, tasks=[*plan.tasks, *followup_tasks])
