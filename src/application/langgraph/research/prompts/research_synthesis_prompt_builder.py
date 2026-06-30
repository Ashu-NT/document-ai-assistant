from src.application.langgraph.research.models import ResearchPlan, ResearchResult
from src.application.langgraph.research.prompts.research_prompt_version import (
    RESEARCH_SYNTHESIS_PROMPT_VERSION,
)


class ResearchSynthesisPromptBuilder:
    prompt_version = RESEARCH_SYNTHESIS_PROMPT_VERSION

    def build(
        self,
        *,
        result: ResearchResult,
        context: dict,
    ) -> str:
        return (
            "Use only the provided evidence.\n"
            "Do not invent facts.\n"
            "Separate findings from missing evidence.\n"
            "Keep page references.\n"
            "Return structured Markdown.\n\n"
            f"Goal: {result.goal.user_input}\n"
            f"Goal type: {result.goal.goal_type.value}\n"
            f"Output type: {result.goal.expected_output_type.value}\n"
            f"Task count: {len(result.plan.tasks)}\n"
            f"Gaps: {len(result.gaps)}\n"
            f"Context:\n{context}\n"
        )
