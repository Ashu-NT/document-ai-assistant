# Phase 2B — Evaluator-Semantics Replay: NOT_ASSERTED Field Fix

**This is NOT a new extraction evaluation run.** No LLM call was made. This
is a deterministic replay of the matcher only, re-run against the exact
`normalized_actual` entity data already recorded by the frozen
`extraction_golden_evaluation_report_reviewed.json` baseline (2026-09-29),
comparing:

- **OLD**: the historical frozen REVIEWED baseline's recorded outcomes
  (`PHASE 2B REVIEWED BASELINE ESTABLISHED` — unchanged, not overwritten).
- **NEW**: the same expectations and the same recorded candidate entities,
  matched under the corrected NOT_ASSERTED/EXPECTED_NULL/EXPECTED_VALUE
  identity semantics (see the implementation report for the code change).

The frozen baseline report files themselves (`extraction_golden_evaluation_report_reviewed.{json,md}`)
were not modified or reinterpreted. This file is a distinct, additional
artifact.

## Method

For each of the 11 REVIEWED expectations, the real `ExtractionExpectationCase`
was reloaded from the actual (unmodified) fixture files — preserving true
key-presence (omitted vs. explicit-null) — and matched against the exact
actual-entity pool the frozen report recorded for that (document, scope,
entity_type) group (every `matched` and `unmatched_actual` entry's
`normalized_actual`, which together constitute the full real candidate
pool that existed during the original run).

## Result

**0 of 11 REVIEWED expectations changed outcome.**

| Case | Old outcome | New outcome | Candidates considered |
|---|---|---|---|
| `extr_core_mtu_cert_manufacturer` | matched | matched | 1 |
| `extr_core_mtu_cert_identifier` | unmatched_expected | unmatched_expected | 0 |
| `extr_mtu_cover_equipment_info` | unmatched_expected | unmatched_expected | 0 |
| `extr_mtu_safety_general_provisions` | unmatched_expected | unmatched_expected | 4 |
| `extr_mtu_task_check_oil_level` | unmatched_expected | unmatched_expected | 12 |
| `extr_mtu_task_visual_inspection` | unmatched_expected | unmatched_expected | 12 |
| `extr_mtu_fuel_filter_procedure` | unmatched_expected | unmatched_expected | 0 |
| `extr_mtu_fuel_filter_safety_warning_crushing` | matched | matched | 2 |
| `extr_core_fwc12_equipment_info` | unmatched_expected | unmatched_expected | 1 |
| `extr_core_fwc12_safety_warning_biohazard` | unmatched_expected | unmatched_expected | 0 |
| `extr_core_fwc12_specification_tank_capacity` | unmatched_expected | unmatched_expected | 0 |

## Why zero outcomes changed, explained per case

- **6 cases had zero recorded candidates** (nothing of that entity type was
  extracted in that scope during the original run at all) — no matcher
  change of any kind can affect an empty candidate pool.
- **2 cases were already MATCHED** (`extr_core_mtu_cert_manufacturer`,
  `extr_mtu_fuel_filter_safety_warning_crushing`) — both entity types'
  only identity field (`name`, `message` respectively) was always asserted
  in golden truth, so there was never an omitted identity field to relax.
- **2 cases (`extr_mtu_safety_general_provisions`, both MaintenanceTask
  cases) had real candidates recorded, but none with matching content**
  regardless of field omission — the extracted entities were about
  substantively different content (different warnings, different table
  rows), so no identity-field relaxation could bridge that gap.
- **1 case (`extr_core_fwc12_equipment_info`) had exactly one real
  candidate recorded** — this is the closest case to the original
  diagnosis's motivating example, but its blocking issue was a DIFFERENT,
  already-diagnosed problem (`model_number` field-assignment error — the
  model swapped the Serial No. into `model_number`), not the omitted-`name`
  issue this fix addresses. Removing `name` from golden truth (already done
  in the prior human-review round) did not by itself fix the
  `model_number` mismatch, and this fix correctly does not touch that
  separate concern.

## Honest interpretation

This replay does not show the fix "improving metrics" against this
specific historical run — it shows the fix behaving exactly as designed
(confirmed independently by the dedicated unit tests, which do directly
exercise the omitted-field-relaxation behavior in isolation) while
correctly declining to paper over unrelated, still-real extraction
failures (field-assignment errors, complete omissions, wrong content).
None of the 11 REVIEWED cases in this particular historical run happened
to be a "close miss" blocked *solely* by the field-omission issue.
