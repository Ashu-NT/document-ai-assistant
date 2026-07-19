# Bumped to v2: added the grounding_violation field/rule so a hard grounding
# failure can be distinguished from merely-incomplete evidence -- previously
# no LLM-sourced decision could ever populate ReflectionDecision.diagnostics
# ["hard_grounding_violation"], so ReflectionValidator's downgrade paths
# (e.g. "grounded maintenance interval evidence exists, accept anyway")
# fired unconditionally for every LLM decision regardless of correctness.
#
# Bumped to v3: added entailment_score/unsupported_claims so
# AnswerQualityScorer's answer_quality.score can be replaced with a real,
# graded claim-to-evidence faithfulness judgment whenever the reflection LLM
# call succeeds, instead of staying a lexical-overlap proxy even when an LLM
# verdict is available (W9, answering_flow_weakness_remediation_plan.md).
REFLECTION_PROMPT_VERSION = "v3"
