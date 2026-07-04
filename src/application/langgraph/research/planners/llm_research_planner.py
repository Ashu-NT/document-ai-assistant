from __future__ import annotations

from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.services.research_json_parser import (
    ResearchJsonParser,
)
from src.application.langgraph.research.services.research_planning_response_schema import (
    build_research_planning_response_json_schema,
)
from src.application.prompts.research import ResearchPlanningPromptBuilder


class LLMResearchPlanner:
    def __init__(
        self,
        llm_service,
        *,
        prompt_builder: ResearchPlanningPromptBuilder | None = None,
        json_parser: ResearchJsonParser | None = None,
        plan_builder: ResearchPlanBuilder | None = None,
        model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or ResearchPlanningPromptBuilder()
        self.json_parser = json_parser or ResearchJsonParser()
        self.plan_builder = plan_builder or ResearchPlanBuilder()
        self.model = model

    def plan(self, *, goal, policy):
        prompt = self.prompt_builder.build(goal, policy)
        raw_payload = self.llm_service.generate(
            prompt,
            model=self.model,
            response_schema=build_research_planning_response_json_schema(),
        )
        data = self.json_parser.parse_planning_response(raw_payload)
        reason = data.reason or "LLM research planning."
        tasks = []
        for raw_task in data.tasks:
            tasks.append(
                self.plan_builder.build_task(
                    title=raw_task.title,
                    question=raw_task.question,
                    strategy_hint=raw_task.strategy_hint,
                    answer_intent_hint=raw_task.answer_intent_hint,
                    document_id=goal.document_id,
                    required=raw_task.required,
                    depends_on=list(raw_task.depends_on),
                    expected_evidence_type=raw_task.expected_evidence_type,
                    max_results=raw_task.max_results or policy.max_evidence_per_task,
                )
            )
        plan = self.plan_builder.build_plan(
            goal=goal,
            tasks=tasks,
            reason=reason,
            source="llm",
            policy=policy,
        )
        return plan, raw_payload
