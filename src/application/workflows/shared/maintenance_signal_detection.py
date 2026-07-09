from __future__ import annotations

# Canonical union of DeterministicStrategySelector's and ReflectionService's
# previously independent marker lists for "is this asking about maintenance
# interval/frequency" -- the two lists had drifted by exactly one marker each
# ("quarterly" vs. bare "schedule"). This does not touch the broader "general
# maintenance topic" detectors in RetrievalQueryIntentInferer or
# AnswerIntentAnalyzer, which check a materially different, broader concept.
MAINTENANCE_INTERVAL_MARKERS: tuple[str, ...] = (
    "maintenance interval",
    "maintenance intervals",
    "service interval",
    "service intervals",
    "inspection interval",
    "inspection intervals",
    "maintenance schedule",
    "preventive maintenance",
    "how often",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "annual",
    "annually",
    "schedule",
)


def mentions_maintenance_interval(text: str) -> bool:
    return any(marker in text for marker in MAINTENANCE_INTERVAL_MARKERS)
