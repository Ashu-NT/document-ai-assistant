from src.application.langgraph.research.models import (
    ResearchGoal,
    ResearchGoalType,
    ResearchOutputType,
)
from src.application.langgraph.research.planners.llm_research_planner import (
    LLMResearchPlanner,
)
from src.application.langgraph.research.policies import ResearchPolicy


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "response_schema": response_schema,
            }
        )
        return self.response


def test_llm_research_planner_passes_response_schema_and_builds_tasks() -> None:
    llm_service = FakeLLMService(
        '{"reason":"Need separate evidence collection tasks.","tasks":[{"title":"Collect maintenance evidence","question":"What maintenance tasks are described?","strategy_hint":"MAINTENANCE_LOOKUP","answer_intent_hint":"summary","required":true,"depends_on":[],"expected_evidence_type":"maintenance","max_results":3}]}'
    )
    planner = LLMResearchPlanner(llm_service, model="research-model")
    goal = ResearchGoal(
        goal_id="goal-1",
        user_input="summarize maintenance tasks",
        goal_type=ResearchGoalType.SUMMARY,
        document_id="doc-42",
        document_title="FWC12 Manual",
        requires_document=True,
        requires_cross_section_reasoning=False,
        requires_multi_strategy_retrieval=False,
        expected_output_type=ResearchOutputType.SUMMARY,
    )

    plan, raw_payload = planner.plan(goal=goal, policy=ResearchPolicy())

    assert raw_payload.startswith('{"reason"')
    assert plan.source == "llm"
    assert len(plan.tasks) == 1
    assert plan.tasks[0].title == "Collect maintenance evidence"
    assert llm_service.calls[0]["model"] == "research-model"
    assert isinstance(llm_service.calls[0]["response_schema"], dict)
