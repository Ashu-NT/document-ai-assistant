from enum import StrEnum


class GuardrailDisposition(StrEnum):
    """The shared disposition mapping PR 11
    (answering_flow_weakness_remediation_plan.md, closes W8) layers on top
    of the existing per-guardrail `GuardrailDecision` values -- what
    ACTION a finding demands, not just what was found. Ordered by
    escalation severity (see `_SEVERITY_ORDER` in
    `guardrail_disposition_mapper.py`, which this order must stay
    consistent with): a passing check never overrides a failing one when
    combining multiple guardrail results for the same turn.

    - PASS: no issue.
    - WARN: recorded as a diagnostic, answer proceeds unchanged (today's
      behavior for every post-answer guardrail, before this PR).
    - REGENERATE: worth one retry -- the same request, regenerated once,
      might come back clean.
    - CLARIFY: the turn is genuinely ambiguous (e.g. evidence conflicts
      because the user never said which equipment/revision they mean) --
      ask, don't guess or retry.
    - ABSTAIN: do not retry -- regenerating is unlikely to fix a
      structural problem (safety-critical content with insufficient
      evidence, or a REGENERATE that already failed once).
    - BLOCK: reserved for the context/pre-generation/final-response
      stages, which already correctly block via `allowed=False` before
      this PR existed -- not mapped to by any post-answer guardrail today.
    """

    PASS = "pass"
    WARN = "warn"
    REGENERATE = "regenerate"
    CLARIFY = "clarify"
    ABSTAIN = "abstain"
    BLOCK = "block"
