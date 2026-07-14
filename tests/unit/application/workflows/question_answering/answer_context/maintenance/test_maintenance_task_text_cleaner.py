from src.application.workflows.question_answering.answer_context.maintenance.maintenance_task_text_cleaner import (
    clean_task,
)


def test_clean_task_strips_leading_schedule_prefix_markers() -> None:
    assert clean_task("M S A=Check gearbox for leaks") == "Check gearbox for leaks"

