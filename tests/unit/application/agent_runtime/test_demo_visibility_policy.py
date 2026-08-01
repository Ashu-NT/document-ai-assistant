from src.application.agent_runtime.policies import DemoVisibilityPolicy
from src.config.settings import langgraph_settings


def test_visibility_policy_defaults_hide_raw_fields() -> None:
    policy = DemoVisibilityPolicy()

    assert policy.show_raw_evidence is False
    assert policy.show_raw_json is False
    assert policy.show_raw_prompts is False
    assert policy.show_internal_ids is False
    assert policy.debug is False


def test_visibility_policy_show_research_plan_reflects_settings(monkeypatch) -> None:
    monkeypatch.setattr(langgraph_settings, "show_research_plan", False)

    policy = DemoVisibilityPolicy()

    assert policy.show_research_plan is False


def test_visibility_policy_show_retrieval_strategy_reflects_settings(monkeypatch) -> None:
    monkeypatch.setattr(langgraph_settings, "show_retrieval_strategy", False)

    policy = DemoVisibilityPolicy()

    assert policy.show_retrieval_strategy is False


def test_visibility_policy_show_reflection_reflects_reflection_show_setting(monkeypatch) -> None:
    monkeypatch.setattr(langgraph_settings, "reflection_show", False)

    policy = DemoVisibilityPolicy()

    assert policy.show_reflection is False
