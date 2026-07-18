# Bumped to v2: added the grounding_violation field/rule so a hard grounding
# failure can be distinguished from merely-incomplete evidence -- previously
# no LLM-sourced decision could ever populate ReflectionDecision.diagnostics
# ["hard_grounding_violation"], so ReflectionValidator's downgrade paths
# (e.g. "grounded maintenance interval evidence exists, accept anyway")
# fired unconditionally for every LLM decision regardless of correctness.
REFLECTION_PROMPT_VERSION = "v2"
