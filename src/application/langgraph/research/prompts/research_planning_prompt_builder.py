from src.application.langgraph.research.models import ResearchGoal
from src.application.langgraph.research.policies import ResearchPolicy
from src.application.langgraph.research.prompts.research_prompt_version import (
    RESEARCH_PLANNING_PROMPT_VERSION,
)


class ResearchPlanningPromptBuilder:
    prompt_version = RESEARCH_PLANNING_PROMPT_VERSION

    def build(
        self,
        goal: ResearchGoal,
        policy: ResearchPolicy,
    ) -> str:
        return (
            "You are a document research planner.\n"
            "Return JSON only.\n"
            "Do not execute tools.\n"
            "Do not invent tools.\n"
            f"Maximum tasks: {policy.max_tasks}\n"
            "Allowed strategy hints are retrieval strategy names such as "
            "MAINTENANCE_LOOKUP, TECHNICAL_SPECIFICATION, IDENTIFIER_LOOKUP, PROCEDURE_LOOKUP, "
            "TROUBLESHOOTING_LOOKUP, CERTIFICATION_LOOKUP, DRAWING_LOOKUP, "
            "FIGURE_LOOKUP, TABLE_LOOKUP, SECTION_LOOKUP, GENERAL_HYBRID.\n"
            "The response schema is:\n"
            "{\n"
            '  "goal_type": "comparison",\n'
            '  "reason": "Why these tasks are needed.",\n'
            '  "tasks": [\n'
            "    {\n"
            '      "task_id": "task_1",\n'
            '      "title": "Collect maintenance tasks",\n'
            '      "question": "What maintenance tasks are described?",\n'
            '      "strategy_hint": "MAINTENANCE_LOOKUP",\n'
            '      "required": true,\n'
            '      "depends_on": []\n'
            "    }\n"
            "  ]\n"
            "}\n"
            f"User request: {goal.user_input}\n"
            f"Document title: {goal.document_title or '-'}\n"
            f"Expected output type: {goal.expected_output_type.value}\n"
        )
