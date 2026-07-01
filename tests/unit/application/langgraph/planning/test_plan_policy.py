from src.application.langgraph.planning import PlanPolicy


def test_plan_policy_default_allows_read_only_tools() -> None:
    policy = PlanPolicy.default()

    assert "list_documents" in policy.allowed_tools
    assert "find_document" in policy.allowed_tools
    assert "answer_question" in policy.allowed_tools


def test_plan_policy_default_allows_retrieve_identifiers() -> None:
    policy = PlanPolicy.default()

    assert "retrieve_identifiers" in policy.allowed_tools


def test_plan_policy_retrieve_identifiers_not_blocked() -> None:
    policy = PlanPolicy.default()

    assert "retrieve_identifiers" not in policy.blocked_tools


def test_plan_policy_default_blocks_mutating_tools() -> None:
    policy = PlanPolicy.default()

    assert "ingest_document" in policy.blocked_tools
    assert "reingest_document" in policy.blocked_tools
    assert "delete_document" in policy.blocked_tools
    assert policy.allow_mutating_tools is False


def test_plan_policy_default_enforces_max_steps() -> None:
    policy = PlanPolicy.default()

    assert policy.max_steps == 5
    assert policy.max_tool_arg_chars == 2000
