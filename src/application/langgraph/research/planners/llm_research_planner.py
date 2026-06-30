from __future__ import annotations

from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.prompts import (
    ResearchPlanningPromptBuilder,
)
from src.application.langgraph.research.services.research_json_parser import (
    ResearchJsonParser,
)


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
        raw_payload = self.llm_service.generate(prompt, model=self.model)
        data = self.json_parser.parse_object(
            raw_payload,
            message_prefix="research planning response",
        )
        reason = str(data.get("reason") or "").strip() or "LLM research planning."
        tasks = []
        for raw_task in list(data.get("tasks") or []):
            if not isinstance(raw_task, dict):
                continue
            tasks.append(
                self.plan_builder.build_task(
                    title=str(raw_task.get("title") or "").strip(),
                    question=str(raw_task.get("question") or "").strip(),
                    strategy_hint=_optional_str(raw_task.get("strategy_hint")),
                    answer_intent_hint=_optional_str(raw_task.get("answer_intent_hint")),
                    document_id=goal.document_id,
                    required=bool(raw_task.get("required", True)),
                    depends_on=[
                        str(item)
                        for item in list(raw_task.get("depends_on") or [])
                        if str(item).strip()
                    ],
                    expected_evidence_type=_optional_str(
                        raw_task.get("expected_evidence_type")
                    ),
                    max_results=int(raw_task.get("max_results") or policy.max_evidence_per_task),
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


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
