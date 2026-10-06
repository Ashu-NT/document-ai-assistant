from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from src.application.workflows.extraction.table_windowing.table_window_activation_policy import (
    TableWindowActivationPolicy,
)
from src.domain.assets import TableAsset

_HEADER = ["Row ID", "Component", "Description"]


def _make_table(row_count: int) -> TableAsset:
    data_rows = [
        [f"ID{n:03d}", f"Component {n}", f"Description of task {n}"]
        for n in range(1, row_count + 1)
    ]
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="irrelevant",
        rows=[_HEADER, *data_rows],
    )


def _policy(**overrides) -> TableWindowActivationPolicy:
    defaults = {"enabled": True, "rows_per_window": 10}
    defaults.update(overrides)
    return TableWindowActivationPolicy(**defaults)


def test_activates_for_maintenance_task_specialized_large_table() -> None:
    policy = _policy()

    assert policy.should_window(
        entity_type=ExtractionPromptType.MAINTENANCE_TASK,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        table=_make_table(39),
    ) is True


def test_does_not_activate_when_disabled() -> None:
    policy = _policy(enabled=False)

    assert policy.should_window(
        entity_type=ExtractionPromptType.MAINTENANCE_TASK,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        table=_make_table(39),
    ) is False


def test_does_not_activate_under_multi_family() -> None:
    policy = _policy()

    assert policy.should_window(
        entity_type=ExtractionPromptType.MAINTENANCE_TASK,
        execution_strategy=ExtractionExecutionStrategy.MULTI_FAMILY,
        table=_make_table(39),
    ) is False


def test_does_not_activate_for_unactivated_entity_family() -> None:
    # Default activation set is {MAINTENANCE_TASK} only - Specification must
    # remain unaffected until a future, separate policy decision enables it.
    policy = _policy()

    assert policy.should_window(
        entity_type=ExtractionPromptType.SPECIFICATION,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        table=_make_table(39),
    ) is False


def test_does_not_activate_for_a_table_at_or_under_the_row_threshold() -> None:
    policy = _policy(rows_per_window=10)

    assert policy.should_window(
        entity_type=ExtractionPromptType.MAINTENANCE_TASK,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        table=_make_table(10),
    ) is False


def test_does_not_activate_when_table_is_none() -> None:
    policy = _policy()

    assert policy.should_window(
        entity_type=ExtractionPromptType.MAINTENANCE_TASK,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        table=None,
    ) is False


def test_activation_set_is_extensible_without_rewriting_the_policy_class() -> None:
    # Future family enablement should be a construction-time/config
    # decision, never a change to the policy's own logic.
    policy = _policy(
        activated_entity_types=frozenset(
            {ExtractionPromptType.MAINTENANCE_TASK, ExtractionPromptType.SPECIFICATION}
        )
    )

    assert policy.should_window(
        entity_type=ExtractionPromptType.SPECIFICATION,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        table=_make_table(39),
    ) is True
