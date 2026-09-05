from __future__ import annotations

"""
Automates `scripts/check_answer_quality_regression.py` (W10) as a real,
discoverable pytest workflow rather than a script only a human remembers to
run by hand (W10b, answering_flow_weakness_remediation_plan.md).

Deliberately marked `slow` (and `e2e`, since it exercises the real
retrieval/answer-generation pipeline end to end) so it is never picked up by
the fast `tests/unit/` suite -- it requires a locally reachable Ollama
instance and runs the real golden-set judge pass, exactly like
`scripts/run_answer_quality_judge.py` itself.

Usage:
    $env:RUN_LIVE_ANSWER_QUALITY_E2E="true"
    pytest -m slow tests/e2e/test_answer_quality_regression_gate.py
"""

import os

from tests.unit.cli_scripts._test_cli_scripts_part1 import _load_script

import pytest


_RUN_LIVE_ANSWER_QUALITY_E2E = (
    os.getenv("RUN_LIVE_ANSWER_QUALITY_E2E", "").strip().lower()
    in {"1", "true", "yes", "on"}
)


@pytest.mark.slow
@pytest.mark.e2e
@pytest.mark.skipif(
    not _RUN_LIVE_ANSWER_QUALITY_E2E,
    reason=(
        "requires a seeded corpus, live Ollama runtime, and answer-quality "
        "baseline; set RUN_LIVE_ANSWER_QUALITY_E2E=true to run"
    ),
)
def test_answer_quality_has_not_regressed_against_the_stored_baseline() -> None:
    mod = _load_script("check_answer_quality_regression")
    exit_code = mod.main([])
    assert exit_code == 0, (
        "Answer-quality regression gate failed -- see the printed report "
        "above for the score/regression detail, or run "
        "`python scripts/check_answer_quality_regression.py` directly."
    )
