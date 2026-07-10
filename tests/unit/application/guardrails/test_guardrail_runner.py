from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.guardrails.guardrail_runner import GuardrailRunner


class _FakeGuardrail:
    def __init__(self, result: GuardrailResult) -> None:
        self._result = result
        self.calls = 0

    def check(self, context: GuardrailContext) -> GuardrailResult:
        self.calls += 1
        return self._result


def _allow(reason: str = "ok") -> GuardrailResult:
    return GuardrailResult(decision=GuardrailDecision.ALLOW, allowed=True, reason=reason)


def _allow_with_violation(reason: str = "warned") -> GuardrailResult:
    from src.application.contracts.guardrails.guardrail_violation import (
        GuardrailViolation,
    )
    from src.application.contracts.guardrails.violation_type import ViolationType

    return GuardrailResult(
        decision=GuardrailDecision.UNSUPPORTED_CLAIMS,
        allowed=True,
        reason=reason,
        violations=[
            GuardrailViolation(
                violation_type=ViolationType.UNSUPPORTED_CLAIM,
                description="warned",
            )
        ],
    )


def _block(reason: str = "blocked") -> GuardrailResult:
    return GuardrailResult(decision=GuardrailDecision.BLOCK, allowed=False, reason=reason)


def test_run_returns_none_when_all_guardrails_pass() -> None:
    runner = GuardrailRunner([_FakeGuardrail(_allow()), _FakeGuardrail(_allow())])

    assert runner.run(GuardrailContext()) is None


def test_run_returns_first_blocking_result_and_stops() -> None:
    third = _FakeGuardrail(_allow())
    runner = GuardrailRunner(
        [_FakeGuardrail(_allow()), _FakeGuardrail(_block()), third]
    )

    result = runner.run(GuardrailContext())

    assert result is not None
    assert result.allowed is False
    assert third.calls == 0


def test_run_ignores_non_blocking_violations() -> None:
    """run() only reports blocking results -- a warn-only ALLOW result with
    violations must not be surfaced by run(), confirming callers that need
    those violations (plan section 9.6) must use run_all() instead."""
    runner = GuardrailRunner([_FakeGuardrail(_allow_with_violation())])

    assert runner.run(GuardrailContext()) is None


def test_run_all_returns_every_result_including_non_blocking_ones() -> None:
    warn = _allow_with_violation()
    guardrails = [_FakeGuardrail(_allow()), _FakeGuardrail(warn), _FakeGuardrail(_block())]
    runner = GuardrailRunner(guardrails)

    results = runner.run_all(GuardrailContext())

    assert len(results) == 3
    assert results[1] is warn
    assert results[1].violations
    assert results[2].allowed is False


def test_run_all_calls_every_guardrail_even_after_a_blocking_one() -> None:
    third = _FakeGuardrail(_allow())
    runner = GuardrailRunner([_FakeGuardrail(_block()), third])

    runner.run_all(GuardrailContext())

    assert third.calls == 1
