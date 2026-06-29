from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.planning import LLMPlanProposer, PlanPolicy
from src.application.langgraph.routing import RouteDecision, RouteType
from src.application.langgraph.state import build_agent_state


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[tuple[str, str | None]] = []

    def generate(self, prompt: str, model: str | None = None) -> str:
        self.prompts.append((prompt, model))
        return self.response


def test_llm_plan_proposer_returns_raw_text_and_tracks_diagnostics() -> None:
    llm_service = FakeLLMService('{"goal":"x","steps":[{"step_id":"step_1","tool_name":"find_document","description":"Find document","args":{"query_text":"pump"},"output_key":"lookup","depends_on":[],"required":true}]}')
    proposer = LLMPlanProposer(llm_service, model="planner-model")

    raw_text = proposer.propose(
        build_agent_state(user_input="Find the pump manual and summarize it."),
        RouteDecision(
            route_type=RouteType.PLANNED_TASK,
            confidence=0.8,
            reason="Compound request needs a plan.",
            extracted_question="Find the pump manual and summarize it.",
            is_compound=True,
            requires_plan=True,
        ),
        ToolRegistry(find_document_tool=object()),
        PlanPolicy.default(),
    )

    assert raw_text.startswith('{"goal"')
    assert llm_service.prompts
    assert llm_service.prompts[0][1] == "planner-model"
    assert proposer.last_diagnostics["model_used"] == "planner-model"
    assert proposer.last_diagnostics["prompt_version"] == "v1"
    assert proposer.last_diagnostics["elapsed_ms"] >= 0
