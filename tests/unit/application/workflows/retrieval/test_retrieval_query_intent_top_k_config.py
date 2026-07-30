from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_query_intent_top_k_config import (
    intent_top_k_overrides,
)


def test_intent_top_k_overrides_loads_shipped_config() -> None:
    result = intent_top_k_overrides()

    assert result[RetrievalQueryIntent.TROUBLESHOOTING] > result[RetrievalQueryIntent.IDENTIFIER]


def test_intent_top_k_overrides_config_path_override(tmp_path) -> None:
    config_path = tmp_path / "intent_top_k.yaml"
    config_path.write_text(
        "overrides:\n  identifier: 2\n  procedure: 9\n",
        encoding="utf-8",
    )

    result = intent_top_k_overrides(config_path=config_path)

    assert result == {
        RetrievalQueryIntent.IDENTIFIER: 2,
        RetrievalQueryIntent.PROCEDURE: 9,
    }


def test_intent_top_k_overrides_ignores_unknown_intent_keys(tmp_path) -> None:
    config_path = tmp_path / "intent_top_k.yaml"
    config_path.write_text(
        "overrides:\n  identifier: 2\n  not_a_real_intent: 5\n",
        encoding="utf-8",
    )

    result = intent_top_k_overrides(config_path=config_path)

    assert result == {RetrievalQueryIntent.IDENTIFIER: 2}
