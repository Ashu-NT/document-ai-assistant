from src.application.langgraph.evaluation import AgentEvalThresholds


def test_agent_eval_thresholds_load_from_yaml(tmp_path) -> None:
    path = tmp_path / "thresholds.yaml"
    path.write_text(
        """
route_accuracy: 0.8
unsafe_block_rate: 0.95
""".strip(),
        encoding="utf-8",
    )

    thresholds = AgentEvalThresholds.from_yaml(path)

    assert thresholds.route_accuracy == 0.8
    assert thresholds.unsafe_block_rate == 0.95
    assert thresholds.plan_validity_rate is None
