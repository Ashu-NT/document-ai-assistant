from src.application.agent_runtime.policies import DemoVisibilityPolicy


def test_visibility_policy_defaults_hide_raw_fields() -> None:
    policy = DemoVisibilityPolicy()

    assert policy.show_raw_json is False
    assert policy.show_raw_prompts is False
    assert policy.show_internal_ids is False
    assert policy.debug is False
