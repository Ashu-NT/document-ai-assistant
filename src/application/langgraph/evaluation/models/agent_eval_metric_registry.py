"""Single ordered registry of agent-eval metric names.

Before this module existed, the same metric-name list was hand-spelled in
4-5 places: a dead ``_METRIC_NAMES`` tuple in ``agent_eval_runner.py``
(confirmed unused - deleted rather than migrated), ``_build_summary``'s
per-metric ``_average_metric(...)`` calls, the ``AgentEvalSummary``
dataclass fields, the ``AgentEvalThresholds`` dataclass fields (plus its
``from_yaml`` keys), and ``AgentQualityGate.check``'s
``(metric, actual, threshold)`` triples.

``AgentEvalSummary`` tracks every metric below; ``AgentEvalThresholds`` (and
therefore the quality gate) only has a configurable threshold for the
subset marked ``has_threshold=True`` - the guardrail/prompt-injection/
grounding metrics are summary-only signals with no pass/fail gate today.

The two dataclasses themselves are intentionally left hand-written rather
than generated from this registry: their field sets differ (the summary
dataclass also carries ``case_count``/``passed_count``/``failed_count``,
and only some metrics have a threshold counterpart), and metaprogramming
dataclass fields from a runtime list would be a speculative abstraction
this refactor doesn't need in order to remove the actual duplication (the
repeated call-site lists in the summary builder and the quality gate).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AgentEvalMetricDefinition:
    name: str
    has_threshold: bool = True


AGENT_EVAL_METRIC_DEFINITIONS: tuple[AgentEvalMetricDefinition, ...] = (
    AgentEvalMetricDefinition("route_accuracy"),
    AgentEvalMetricDefinition("deep_research_route_accuracy"),
    AgentEvalMetricDefinition("document_selection_accuracy"),
    AgentEvalMetricDefinition("clarification_accuracy"),
    AgentEvalMetricDefinition("unsafe_block_rate"),
    AgentEvalMetricDefinition("guardrail_block_rate", has_threshold=False),
    AgentEvalMetricDefinition("out_of_scope_redirect_rate", has_threshold=False),
    AgentEvalMetricDefinition("false_positive_guardrail_rate", has_threshold=False),
    AgentEvalMetricDefinition("false_negative_guardrail_rate", has_threshold=False),
    AgentEvalMetricDefinition("prompt_injection_block_rate", has_threshold=False),
    AgentEvalMetricDefinition("destructive_tool_block_rate", has_threshold=False),
    AgentEvalMetricDefinition("grounding_failure_catch_rate", has_threshold=False),
    AgentEvalMetricDefinition("plan_validity_rate"),
    AgentEvalMetricDefinition("document_scope_safety_rate"),
    AgentEvalMetricDefinition("tool_policy_compliance_rate"),
    AgentEvalMetricDefinition("answer_expectation_rate"),
    AgentEvalMetricDefinition("retrieval_strategy_selection_rate"),
    AgentEvalMetricDefinition("retrieval_strategy_validity_rate"),
    AgentEvalMetricDefinition("strategy_fallback_rate"),
    AgentEvalMetricDefinition("multi_strategy_success_rate"),
    AgentEvalMetricDefinition("strategy_document_scope_safety_rate"),
    AgentEvalMetricDefinition("strategy_trace_coverage_rate"),
    AgentEvalMetricDefinition("research_plan_validity_rate"),
    AgentEvalMetricDefinition("research_task_success_rate"),
    AgentEvalMetricDefinition("research_gap_detection_rate"),
    AgentEvalMetricDefinition("research_document_scope_safety_rate"),
    AgentEvalMetricDefinition("research_report_completeness_rate"),
    AgentEvalMetricDefinition("research_citation_coverage_rate"),
)

# All tracked metric names, in a stable order (used by the summary builder).
AGENT_EVAL_METRIC_NAMES: tuple[str, ...] = tuple(
    definition.name for definition in AGENT_EVAL_METRIC_DEFINITIONS
)

# Metric names with a configurable quality-gate threshold, in the same
# order as `AgentEvalThresholds`'s fields (used by `AgentQualityGate.check`).
AGENT_EVAL_THRESHOLD_METRIC_NAMES: tuple[str, ...] = tuple(
    definition.name
    for definition in AGENT_EVAL_METRIC_DEFINITIONS
    if definition.has_threshold
)
