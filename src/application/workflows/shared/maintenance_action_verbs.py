from __future__ import annotations

# Canonical maintenance action-verb list, previously independently spelled
# out (identically) inside KeyValueExtractor's and MaintenanceEntryMerger's
# private regex patterns. Each consumer still compiles its own regex from
# this tuple -- the anchoring/flags/grouping differ per call site.
MAINTENANCE_ACTION_VERBS: tuple[str, ...] = (
    "inspect",
    "check",
    "replace",
    "lubricate",
    "clean",
    "test",
    "drain",
    "tighten",
    "calibrate",
    "change",
    "grease",
    "service",
    "flush",
    "verify",
    "examine",
    "adjust",
    "renew",
)
