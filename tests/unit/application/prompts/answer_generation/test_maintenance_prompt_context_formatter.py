from src.application.prompts.answer_generation.maintenance_prompt_context_formatter import (
    MaintenancePromptContextFormatter,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
)


def test_formatter_uses_reference_derived_properties_after_phase2_refactor() -> None:
    formatter = MaintenancePromptContextFormatter()
    entry = AnswerMaintenanceEntry(
        task="Replace filter cartridge",
        description="Replace filter cartridge and inspect seals",
        interval="Every 500 hours",
        component="filter cartridge",
        notes=None,
        source_number=99,
        references=[
            AnswerMaintenanceReference(
                source_number=3,
                page_start=12,
                page_end=12,
                section_path="Maintenance > Filters",
            ),
            AnswerMaintenanceReference(
                source_number=5,
                page_start=14,
                page_end=15,
                section_path="Maintenance > Preventive Maintenance",
            ),
        ],
    )

    lines = formatter.format([entry])
    rendered = "\n".join(lines)

    assert entry.source_number == 3
    assert "Pages 12, 14-15" in rendered
    assert "Sections:" in rendered
    assert "Maintenance > Filters" in rendered
    assert "Maintenance > Preventive Maintenance" in rendered
    assert "Sources: SOURCE 3, SOURCE 5" in rendered
