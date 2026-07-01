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
            "\n"
            "Allowed strategy hints and when to use each:\n"
            "- IDENTIFIER_LOOKUP: Use when the question references a specific identifier such as a part number,\n"
            "  serial number, model number, order code, drawing number, or tag number (e.g. 'HP-001', 'SN-2024').\n"
            "  Frame the task question as: 'What evidence describes identifier [value]?'\n"
            "- MAINTENANCE_LOOKUP: Use for maintenance schedules, service intervals, lubrication, inspection tasks.\n"
            "- TECHNICAL_SPECIFICATION: Use for pressure, temperature, voltage, dimensions, material, ratings.\n"
            "- PROCEDURE_LOOKUP: Use for startup, shutdown, installation, replacement, commissioning steps.\n"
            "- TROUBLESHOOTING_LOOKUP: Use for faults, alarms, symptoms, causes, remedies.\n"
            "- CERTIFICATION_LOOKUP: Use for ATEX, IECEx, CE, approval certificates, compliance.\n"
            "- DRAWING_LOOKUP: Use for drawings, schematics, diagrams, layouts, title blocks.\n"
            "- FIGURE_LOOKUP: Use for figures, images, pictures.\n"
            "- TABLE_LOOKUP: Use for tables, matrices, ordering examples, structured lists.\n"
            "- SECTION_LOOKUP: Use for overview sections, scope, introduction, general context.\n"
            "- GENERAL_HYBRID: Use when no specific strategy applies or the question spans multiple areas.\n"
            "\n"
            "The response schema is:\n"
            "{\n"
            '  "goal_type": "comparison",\n'
            '  "reason": "Why these tasks are needed.",\n'
            '  "tasks": [\n'
            "    {\n"
            '      "task_id": "task_1",\n'
            '      "title": "Collect identifier evidence for HP-001",\n'
            '      "question": "What evidence in this document describes identifier HP-001?",\n'
            '      "strategy_hint": "IDENTIFIER_LOOKUP",\n'
            '      "required": true,\n'
            '      "depends_on": []\n'
            "    }\n"
            "  ]\n"
            "}\n"
            f"User request: {goal.user_input}\n"
            f"Document title: {goal.document_title or '-'}\n"
            f"Expected output type: {goal.expected_output_type.value}\n"
        )
